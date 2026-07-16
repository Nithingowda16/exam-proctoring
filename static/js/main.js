// Common JavaScript Utilities

document.addEventListener("DOMContentLoaded", () => {
    // Auto-dismiss standard alerts after 5 seconds
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.style.transition = "opacity 0.5s ease";
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Confirmation bindings for deletion forms
    const confirmDeleteForms = document.querySelectorAll("form[data-confirm-delete]");
    confirmDeleteForms.forEach((form) => {
        form.addEventListener("submit", (e) => {
            const msg = form.dataset.confirmDelete || "Are you sure you want to delete this item?";
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });
});
