// Secure Examination Engine

document.addEventListener("DOMContentLoaded", () => {
    // Check if we are on the exam page (session ID element exists)
    const examContainer = document.getElementById("exam-page-container");
    if (!examContainer) return;

    // Retrieve state parameters
    const sessionId = parseInt(examContainer.dataset.sessionId);
    let remainingSeconds = parseInt(examContainer.dataset.remainingSeconds);
    const totalQuestions = parseInt(examContainer.dataset.totalQuestions);
    
    let currentIdx = 0;
    let isSubmitting = false;
    let warningModalOpen = false;
    let isCameraInitializing = false;

    // DOM Elements
    const qContainers = document.querySelectorAll(".question-block");
    const navItems = document.querySelectorAll(".nav-item");
    const prevBtn = document.getElementById("prev-btn");
    const nextBtn = document.getElementById("next-btn");
    const clearBtn = document.getElementById("clear-btn");
    const reviewBtn = document.getElementById("review-btn");
    const timerDisplay = document.getElementById("timer-display");
    const progressBar = document.getElementById("progress-bar");
    const submitForm = document.getElementById("exam-submit-form");
    
    // Warning Modal
    const warningModal = document.getElementById("warning-modal");
    const warningTitle = document.getElementById("warning-title");
    const warningText = document.getElementById("warning-text");
    const warningConfirmBtn = document.getElementById("warning-confirm-btn");

    // ----------------- Pagination & Navigation -----------------
    function showQuestion(index) {
        if (index < 0 || index >= totalQuestions) return;
        
        // Hide all blocks, show the active one
        qContainers.forEach((block, idx) => {
            if (idx === index) {
                block.classList.remove("d-none");
            } else {
                block.classList.add("d-none");
            }
        });

        // Update Nav Grid highlight
        navItems.forEach((item, idx) => {
            if (idx === index) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        });

        currentIdx = index;

        // Button states
        prevBtn.disabled = (currentIdx === 0);
        if (currentIdx === totalQuestions - 1) {
            nextBtn.innerHTML = 'Finish <span style="margin-left:4px;">→</span>';
        } else {
            nextBtn.innerHTML = 'Next <span style="margin-left:4px;">→</span>';
        }

        updateProgress();
    }

    // Previous and Next button click events
    prevBtn.addEventListener("click", () => {
        if (currentIdx > 0) showQuestion(currentIdx - 1);
    });

    nextBtn.addEventListener("click", () => {
        if (currentIdx < totalQuestions - 1) {
            showQuestion(currentIdx + 1);
        } else {
            // Confirm submit
            confirmSubmit();
        }
    });

    // Nav grid clicks
    navItems.forEach((item) => {
        item.addEventListener("click", (e) => {
            const index = parseInt(e.target.dataset.index);
            showQuestion(index);
        });
    });

    // ----------------- Auto-Save and Selection Logic -----------------
    qContainers.forEach((container) => {
        const questionId = parseInt(container.dataset.questionId);
        const options = container.querySelectorAll(".option-item");
        
        options.forEach((opt) => {
            opt.addEventListener("click", () => {
                const selectedOptionId = parseInt(opt.dataset.optionId);
                
                // Toggle active visual state
                options.forEach(o => o.classList.remove("selected"));
                opt.classList.add("selected");
                
                // Update nav item class
                const navItem = document.querySelector(`.nav-item[data-q-id="${questionId}"]`);
                if (navItem) {
                    navItem.classList.add("answered");
                }
                
                // Call API
                sendSaveRequest(questionId, selectedOptionId);
            });
        });
    });

    // Clear Selection
    clearBtn.addEventListener("click", () => {
        const activeContainer = qContainers[currentIdx];
        const questionId = parseInt(activeContainer.dataset.questionId);
        const options = activeContainer.querySelectorAll(".option-item");
        
        options.forEach(o => o.classList.remove("selected"));
        
        const navItem = document.querySelector(`.nav-item[data-q-id="${questionId}"]`);
        if (navItem) {
            navItem.classList.remove("answered");
        }
        
        sendSaveRequest(questionId, null);
    });

    // Send Save Answer request
    function sendSaveRequest(questionId, selectedOptionId) {
        fetch("/api/save_answer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: sessionId,
                question_id: questionId,
                selected_option_id: selectedOptionId
            })
        })
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                console.error("Save failed:", data.error);
            }
            updateProgress();
        })
        .catch(err => console.error("Error saving answer:", err));
    }

    // Mark For Review
    reviewBtn.addEventListener("click", () => {
        const activeContainer = qContainers[currentIdx];
        const questionId = parseInt(activeContainer.dataset.questionId);
        const navItem = document.querySelector(`.nav-item[data-q-id="${questionId}"]`);
        
        if (!navItem) return;
        
        const isCurrentlyReview = navItem.classList.contains("review");
        
        if (isCurrentlyReview) {
            navItem.classList.remove("review");
        } else {
            navItem.classList.add("review");
        }
        
        fetch("/api/mark_review", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: sessionId,
                question_id: questionId,
                marked: !isCurrentlyReview
            })
        })
        .then(res => res.json())
        .catch(err => console.error("Error marking for review:", err));
    });

    // Update progress bar
    function updateProgress() {
        const answered = document.querySelectorAll(".nav-item.answered").length;
        const percent = (answered / totalQuestions) * 100;
        progressBar.style.width = `${percent}%`;
    }

    // ----------------- Countdown Timer -----------------
    function updateTimerDisplay() {
        if (remainingSeconds <= 0) {
            timerDisplay.textContent = "00:00";
            timerDisplay.classList.add("warning-timer");
            triggerAutoSubmit("Time Expired");
            return;
        }

        const mins = Math.floor(remainingSeconds / 60);
        const secs = remainingSeconds % 60;
        timerDisplay.textContent = `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;

        if (remainingSeconds < 300) { // Under 5 minutes left
            timerDisplay.classList.add("warning-timer");
        }

        remainingSeconds--;
    }

    const timerInterval = setInterval(updateTimerDisplay, 1000);
    updateTimerDisplay(); // Init run

    // ----------------- Submission Confirmations -----------------
    function confirmSubmit() {
        const answered = document.querySelectorAll(".nav-item.answered").length;
        const unanswered = totalQuestions - answered;
        
        let confirmMsg = `Are you sure you want to submit your examination?\n\nTotal Questions: ${totalQuestions}\nAnswered: ${answered}\nUnanswered: ${unanswered}`;
        
        if (unanswered > 0) {
            confirmMsg += `\n\nWARNING: You have ${unanswered} unanswered question(s).`;
        }
        
        if (confirm(confirmMsg)) {
            executeFormSubmission();
        }
    }

    function executeFormSubmission() {
        if (isSubmitting) return;
        isSubmitting = true;
        
        // Remove unload event listener before submitting
        window.removeEventListener("beforeunload", preventExit);
        submitForm.submit();
    }

    function triggerAutoSubmit(reason) {
        if (isSubmitting) return;
        isSubmitting = true;
        clearInterval(timerInterval);
        
        alert(`The examination is being submitted automatically. Reason: ${reason}`);
        
        window.removeEventListener("beforeunload", preventExit);
        submitForm.submit();
    }

    // ----------------- Anti-Cheating & Security Features -----------------

    // 1. Unload Guard
    function preventExit(e) {
        e.preventDefault();
        e.returnValue = "Are you sure you want to exit? Your exam progress might be lost.";
        return e.returnValue;
    }
    window.addEventListener("beforeunload", preventExit);

    // Disable Back Button Navigation
    history.pushState(null, null, location.href);
    window.addEventListener('popstate', function () {
        history.pushState(null, null, location.href);
    });

    // 2. Block Context Menu & Selection Actions
    document.addEventListener("contextmenu", e => e.preventDefault());
    document.addEventListener("copy", e => e.preventDefault());
    document.addEventListener("paste", e => e.preventDefault());
    document.addEventListener("cut", e => e.preventDefault());
    document.addEventListener("selectstart", e => e.preventDefault());
    document.addEventListener("dragstart", e => e.preventDefault());

    // 3. Block Keyboard Shortcuts
    document.addEventListener("keydown", (e) => {
        // F12 Key
        if (e.keyCode === 123) {
            e.preventDefault();
            triggerViolation("Shortcut blocked (F12)");
            return false;
        }
        
        // Ctrl+Shift+I, J, C, U (Dev Tools and Source view)
        if (e.ctrlKey && e.shiftKey && (e.keyCode === 73 || e.keyCode === 74 || e.keyCode === 67)) {
            e.preventDefault();
            triggerViolation("Shortcut blocked (Ctrl+Shift+DevTools)");
            return false;
        }

        // Ctrl+U (View Source)
        if (e.ctrlKey && e.keyCode === 85) {
            e.preventDefault();
            triggerViolation("Shortcut blocked (Ctrl+U View Source)");
            return false;
        }

        // Ctrl+P (Print Screen)
        if (e.ctrlKey && e.keyCode === 80) {
            e.preventDefault();
            triggerViolation("Shortcut blocked (Ctrl+P Print)");
            return false;
        }

        // Ctrl+S (Save Page)
        if (e.ctrlKey && e.keyCode === 83) {
            e.preventDefault();
            triggerViolation("Shortcut blocked (Ctrl+S Save)");
            return false;
        }

        // Ctrl+A (Select All)
        if (e.ctrlKey && e.keyCode === 65) {
            e.preventDefault();
            return false;
        }

        // Prevent refresh shortcuts F5 / Ctrl+R
        if (e.keyCode === 116 || (e.ctrlKey && e.keyCode === 82)) {
            e.preventDefault();
            alert("Refresh disabled during active exam session.");
            return false;
        }
    });

    // 4. Fullscreen Enforcement
    const startFullscreenModal = document.createElement("div");
    startFullscreenModal.classList.add("modal-overlay");
    startFullscreenModal.style.display = "flex";
    startFullscreenModal.innerHTML = `
        <div class="modal-content glass-card">
            <h2>Start Examination Mode</h2>
            <p style="margin: 16px 0; color: var(--text-secondary);">This examination requires Secure Fullscreen Mode. Please click the button below to enter fullscreen and start.</p>
            <button id="enter-fullscreen-btn" class="btn-primary">Enter Fullscreen & Start</button>
        </div>
    `;
    document.body.appendChild(startFullscreenModal);

    const enterFsBtn = document.getElementById("enter-fullscreen-btn");
    enterFsBtn.addEventListener("click", () => {
        enterFullscreen();
        startFullscreenModal.style.display = "none";
        // Initialize proctoring webcam
        initWebcam();
        // Initialize first question display after entering fullscreen
        showQuestion(0);
    });

    function initWebcam() {
        const video = document.getElementById("proctor-video");
        const container = document.getElementById("webcam-container");
        
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Your browser does not support webcam access. Please contact the administrator.");
            triggerViolation("Camera API Not Supported");
            return;
        }
        
        isCameraInitializing = true; // Block window blur violations during browser permission prompt
        
        navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 320 } })
            .then(stream => {
                isCameraInitializing = false;
                video.srcObject = stream;
                container.style.display = "block";
                startFrameUploading();
            })
            .catch(err => {
                isCameraInitializing = false;
                console.error("Camera access error:", err);
                alert("CRITICAL SECURITY VIOLATION: Camera access is mandatory. The exam will now submit automatically.");
                triggerViolation("Webcam Access Denied / Blocked");
                setTimeout(() => {
                    triggerAutoSubmit("Webcam Access Denied / Blocked");
                }, 1500);
            });
    }

    function startFrameUploading() {
        const video = document.getElementById("proctor-video");
        const canvas = document.createElement("canvas");
        canvas.width = 240;
        canvas.height = 180;
        const ctx = canvas.getContext("2d");
        
        setInterval(() => {
            if (isSubmitting || !video.srcObject) return;
            try {
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                const dataUrl = canvas.toDataURL("image/jpeg", 0.5); // 50% quality is highly compressed and tiny
                
                fetch("/api/upload_frame", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        session_id: sessionId,
                        frame: dataUrl
                    })
                });
            } catch (e) {
                console.error("Frame capture error:", e);
            }
        }, 4000);
    }

    function enterFullscreen() {
        const docEl = document.documentElement;
        if (docEl.requestFullscreen) {
            docEl.requestFullscreen();
        } else if (docEl.mozRequestFullScreen) { /* Firefox */
            docEl.mozRequestFullScreen();
        } else if (docEl.webkitRequestFullscreen) { /* Chrome, Safari and Opera */
            docEl.webkitRequestFullscreen();
        } else if (docEl.msRequestFullscreen) { /* IE/Edge */
            docEl.msRequestFullscreen();
        }
    }

    // Monitor Fullscreen Exit
    document.addEventListener("fullscreenchange", checkFullscreenState);
    document.addEventListener("webkitfullscreenchange", checkFullscreenState);
    document.addEventListener("mozfullscreenchange", checkFullscreenState);
    document.addEventListener("MSFullscreenChange", checkFullscreenState);

    function checkFullscreenState() {
        const isFullscreen = document.fullscreenElement || 
                              document.webkitFullscreenElement || 
                              document.mozFullScreenElement || 
                              document.msFullscreenElement;
                              
        if (!isFullscreen && !isSubmitting) {
            triggerViolation("Fullscreen Exit");
        }
    }

    // 5. Tab Switching & Focus Loss Detection
    document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "hidden" && !isSubmitting) {
            triggerViolation("Tab Switching (Visibility Hidden)");
        }
    });

    window.addEventListener("blur", () => {
        if (!isSubmitting && !warningModalOpen && !isCameraInitializing) {
            triggerViolation("Window Focus Lost");
        }
    });

    // 6. Violation logging logic
    function triggerViolation(type) {
        if (isSubmitting) return;

        fetch("/api/log_violation", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: sessionId,
                violation_type: type
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                if (data.auto_submit) {
                    triggerAutoSubmit(`Cheating Violation Limit Exceeded (${type})`);
                } else {
                    showWarningPopup(data.warning_number, type);
                }
            }
        })
        .catch(err => console.error("Error logging violation:", err));
    }

    // Warning alert model popups
    function showWarningPopup(warningNum, type) {
        warningModalOpen = true;
        warningModal.style.display = "flex";
        
        if (warningNum === 1) {
            warningTitle.textContent = "WARNING: Violation Detected";
            warningTitle.className = "text-warning";
            warningText.innerHTML = `You have triggered a security warning.<br><strong>Reason:</strong> ${type}<br><br>First warning logged. Exiting fullscreen, switching tabs, or losing focus is strictly prohibited.`;
        } else if (warningNum === 2) {
            warningTitle.textContent = "FINAL WARNING";
            warningTitle.className = "text-danger";
            warningText.innerHTML = `You have triggered a final security warning.<br><strong>Reason:</strong> ${type}<br><br><strong>CRITICAL:</strong> A third violation will result in the immediate and automatic submission of your examination!`;
        }
    }

    warningConfirmBtn.addEventListener("click", () => {
        warningModal.style.display = "none";
        warningModalOpen = false;
        // Force back into fullscreen
        enterFullscreen();
    });
});
