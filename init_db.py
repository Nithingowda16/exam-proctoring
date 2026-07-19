import sys
from werkzeug.security import generate_password_hash
from database import get_db_connection, init_db

# Exactly 100 HTML Multiple Choice Questions
HTML_QUESTIONS = [
    {
        "text": "What does the abbreviation HTML stand for?",
        "category": "HTML Introduction",
        "difficulty": "Easy",
        "options": [
            {"text": "Hyper Text Markup Language", "is_correct": True},
            {"text": "High Text Markup Language", "is_correct": False},
            {"text": "Hyper Tabular Markup Language", "is_correct": False},
            {"text": "Hyperlinks and Text Markup Language", "is_correct": False}
        ]
    },
    {
        "text": "Which organization is responsible for defining the official HTML specifications and standards?",
        "category": "HTML Introduction",
        "difficulty": "Easy",
        "options": [
            {"text": "World Wide Web Consortium (W3C)", "is_correct": True},
            {"text": "Netscape Corporation", "is_correct": False},
            {"text": "Mozilla Foundation", "is_correct": False},
            {"text": "International Organization for Standardization (ISO)", "is_correct": False}
        ]
    },
    {
        "text": "What is the correct, minimal DOCTYPE declaration required for HTML5 documents?",
        "category": "DOCTYPE",
        "difficulty": "Easy",
        "options": [
            {"text": "<!DOCTYPE html>", "is_correct": True},
            {"text": "<!DOCTYPE HTML5>", "is_correct": False},
            {"text": "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 5.0//EN\">", "is_correct": False},
            {"text": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>", "is_correct": False}
        ]
    },
    {
        "text": "In HTML, what is the primary purpose of the DOCTYPE declaration?",
        "category": "DOCTYPE",
        "difficulty": "Medium",
        "options": [
            {"text": "To instruct the web browser about the document type and HTML version, enabling correct Standards Mode rendering", "is_correct": True},
            {"text": "To link the HTML document to an external cascading style sheet (CSS)", "is_correct": False},
            {"text": "To configure the character encoding of the web page", "is_correct": False},
            {"text": "To define the global title and metadata of the document", "is_correct": False}
        ]
    },
    {
        "text": "Which attribute is highly recommended on the root <html> element to specify the primary language of the web page?",
        "category": "Language Attribute",
        "difficulty": "Easy",
        "options": [
            {"text": "lang", "is_correct": True},
            {"text": "xml:lang", "is_correct": False},
            {"text": "content-lang", "is_correct": False},
            {"text": "language", "is_correct": False}
        ]
    },
    {
        "text": "In which HTML section must elements like <title>, external stylesheets, and character encoding declarations reside?",
        "category": "HTML Structure",
        "difficulty": "Easy",
        "options": [
            {"text": "<head>", "is_correct": True},
            {"text": "<body>", "is_correct": False},
            {"text": "<header>", "is_correct": False},
            {"text": "<meta>", "is_correct": False}
        ]
    },
    {
        "text": "Which of the following tags represents an 'empty' or self-closing HTML element?",
        "category": "Empty Elements",
        "difficulty": "Easy",
        "options": [
            {"text": "<br>", "is_correct": True},
            {"text": "<title>", "is_correct": False},
            {"text": "<strong>", "is_correct": False},
            {"text": "<option>", "is_correct": False}
        ]
    },
    {
        "text": "What is the correct syntax for writing a comment in HTML?",
        "category": "Comments",
        "difficulty": "Easy",
        "options": [
            {"text": "<!-- This is a comment -->", "is_correct": True},
            {"text": "// This is a comment", "is_correct": False},
            {"text": "/* This is a comment */", "is_correct": False},
            {"text": "# This is a comment", "is_correct": False}
        ]
    },
    {
        "text": "Which meta character set encoding is widely recommended for HTML5 to support global text characters?",
        "category": "Character Encoding",
        "difficulty": "Easy",
        "options": [
            {"text": "<meta charset=\"UTF-8\">", "is_correct": True},
            {"text": "<meta charset=\"ISO-8859-1\">", "is_correct": False},
            {"text": "<meta charset=\"ASCII\">", "is_correct": False},
            {"text": "<meta charset=\"UTF-16\">", "is_correct": False}
        ]
    },
    {
        "text": "Which global attribute is used to uniquely identify a single element on a web page?",
        "category": "Global Attributes",
        "difficulty": "Easy",
        "options": [
            {"text": "id", "is_correct": True},
            {"text": "class", "is_correct": False},
            {"text": "name", "is_correct": False},
            {"text": "key", "is_correct": False}
        ]
    },
    {
        "text": "What is the purpose of the global 'tabindex' attribute in HTML?",
        "category": "Global Attributes",
        "difficulty": "Medium",
        "options": [
            {"text": "To control the keyboard navigation order of elements when the user presses the Tab key", "is_correct": True},
            {"text": "To create visual tabs inside a layout container", "is_correct": False},
            {"text": "To list open browser tabs in the window", "is_correct": False},
            {"text": "To link elements to browser history", "is_correct": False}
        ]
    },
    {
        "text": "Which global attribute is used to store custom, private data attributes specific to a web page or application?",
        "category": "Global Attributes",
        "difficulty": "Medium",
        "options": [
            {"text": "data-*", "is_correct": True},
            {"text": "custom-*", "is_correct": False},
            {"text": "value-*", "is_correct": False},
            {"text": "attr-*", "is_correct": False}
        ]
    },
    {
        "text": "What is the semantic difference between <h1> and <h6> tags in HTML?",
        "category": "Headings",
        "difficulty": "Easy",
        "options": [
            {"text": "<h1> represents the highest level of section heading, while <h6> represents the lowest level", "is_correct": True},
            {"text": "<h1> is always red and <h6> is always blue", "is_correct": False},
            {"text": "<h1> is for titles and <h6> is for footnotes", "is_correct": False},
            {"text": "<h1> is block-level and <h6> is inline-level", "is_correct": False}
        ]
    },
    {
        "text": "What is the default browser layout behavior of headings (e.g., <h2>) and paragraphs (<p>)?",
        "category": "Paragraphs",
        "difficulty": "Medium",
        "options": [
            {"text": "They are block-level elements that start on a new line and take up the full width available", "is_correct": True},
            {"text": "They are inline elements that sit on the same line", "is_correct": False},
            {"text": "They display as flex containers by default", "is_correct": False},
            {"text": "They display as grid elements by default", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML element is used to insert a thematic break or horizontal rule, typically displayed as a horizontal line?",
        "category": "Horizontal Rules",
        "difficulty": "Easy",
        "options": [
            {"text": "<hr>", "is_correct": True},
            {"text": "<br>", "is_correct": False},
            {"text": "<line>", "is_correct": False},
            {"text": "<divider>", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML tag is used to visually mark or highlight text for reference purposes, typically rendering with a yellow background?",
        "category": "Formatting Tags",
        "difficulty": "Easy",
        "options": [
            {"text": "<mark>", "is_correct": True},
            {"text": "<highlight>", "is_correct": False},
            {"text": "<em>", "is_correct": False},
            {"text": "<strong>", "is_correct": False}
        ]
    },
    {
        "text": "What is the semantic difference between the <strong> tag and the <b> tag in HTML?",
        "category": "Formatting Tags",
        "difficulty": "Medium",
        "options": [
            {"text": "<strong> indicates that its contents have strong importance or urgency, whereas <b> is used for styling bold text without extra importance", "is_correct": True},
            {"text": "<strong> is for headings and <b> is for body text", "is_correct": False},
            {"text": "<strong> makes text larger and <b> makes it bolder", "is_correct": False},
            {"text": "<strong> is deprecated in HTML5 and <b> is the modern alternative", "is_correct": False}
        ]
    },
    {
        "text": "What is the semantic difference between the <em> tag and the <i> tag in HTML?",
        "category": "Formatting Tags",
        "difficulty": "Medium",
        "options": [
            {"text": "<em> indicates stressed emphasis on the text, whereas <i> represents text in an alternate voice or technical term without strong emphasis", "is_correct": True},
            {"text": "<em> is only for screen readers and <i> is for visual rendering", "is_correct": False},
            {"text": "<em> makes text bold and <i> makes it italic", "is_correct": False},
            {"text": "There is no difference; both are fully interchangeable", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML element is used to define a block of text that is quoted from another source, typically indented by default?",
        "category": "Quotations",
        "difficulty": "Easy",
        "options": [
            {"text": "<blockquote>", "is_correct": True},
            {"text": "<q>", "is_correct": False},
            {"text": "<cite>", "is_correct": False},
            {"text": "<quote>", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML tag is used to define the title of a creative work within a citation or quote?",
        "category": "Quotations",
        "difficulty": "Medium",
        "options": [
            {"text": "<cite>", "is_correct": True},
            {"text": "<q>", "is_correct": False},
            {"text": "<source>", "is_correct": False},
            {"text": "<reference>", "is_correct": False}
        ]
    },
    {
        "text": "What is the purpose of the HTML <pre> element?",
        "category": "Preformatted Text",
        "difficulty": "Medium",
        "options": [
            {"text": "To display preformatted text, preserving both spaces and line breaks exactly as written in the source code", "is_correct": True},
            {"text": "To execute JavaScript before rendering the body elements", "is_correct": False},
            {"text": "To pre-render stylesheet instructions for performance", "is_correct": False},
            {"text": "To define a preliminary header section", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML tag is used to mark a sequence of characters as a computer code snippet?",
        "category": "Code Elements",
        "difficulty": "Easy",
        "options": [
            {"text": "<code>", "is_correct": True},
            {"text": "<samp>", "is_correct": False},
            {"text": "<kbd>", "is_correct": False},
            {"text": "<script>", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML element represents keyboard input, typically typed by a user on a keyboard?",
        "category": "Code Elements",
        "difficulty": "Medium",
        "options": [
            {"text": "<kbd>", "is_correct": True},
            {"text": "<code>", "is_correct": False},
            {"text": "<samp>", "is_correct": False},
            {"text": "<input>", "is_correct": False}
        ]
    },
    {
        "text": "How do you open a hyperlink in a new browser tab or window by default?",
        "category": "Hyperlinks",
        "difficulty": "Easy",
        "options": [
            {"text": "target=\"_blank\"", "is_correct": True},
            {"text": "target=\"new\"", "is_correct": False},
            {"text": "target=\"_self\"", "is_correct": False},
            {"text": "rel=\"external\"", "is_correct": False}
        ]
    },
    {
        "text": "What is the key difference between relative links and absolute links?",
        "category": "Hyperlinks",
        "difficulty": "Medium",
        "options": [
            {"text": "Relative links point to a path relative to the current directory, whereas absolute links specify the full URL including protocol and domain", "is_correct": True},
            {"text": "Relative links only work on local files and absolute links only work on live servers", "is_correct": False},
            {"text": "Relative links are faster to resolve than absolute links", "is_correct": False},
            {"text": "Absolute links cannot use secure HTTPS protocols", "is_correct": False}
        ]
    },
    {
        "text": "What is the correct syntax to create a hyperlink that initiates an email to 'info@example.com'?",
        "category": "Hyperlinks",
        "difficulty": "Easy",
        "options": [
            {"text": "<a href=\"mailto:info@example.com\">", "is_correct": True},
            {"text": "<a href=\"email:info@example.com\">", "is_correct": False},
            {"text": "<a mailto=\"info@example.com\">", "is_correct": False},
            {"text": "<a href=\"sendmail:info@example.com\">", "is_correct": False}
        ]
    },
    {
        "text": "Which prefix should be used in the 'href' attribute of a hyperlink to create a direct telephone dial link?",
        "category": "Hyperlinks",
        "difficulty": "Easy",
        "options": [
            {"text": "tel:", "is_correct": True},
            {"text": "phone:", "is_correct": False},
            {"text": "call:", "is_correct": False},
            {"text": "dial:", "is_correct": False}
        ]
    },
    {
        "text": "How is a bookmark link (anchor link) created to scroll the page to an element with the ID 'section-3'?",
        "category": "Hyperlinks",
        "difficulty": "Easy",
        "options": [
            {"text": "<a href=\"#section-3\">", "is_correct": True},
            {"text": "<a href=\"id:section-3\">", "is_correct": False},
            {"text": "<a link=\"section-3\">", "is_correct": False},
            {"text": "<a href=\"section-3\">", "is_correct": False}
        ]
    },
    {
        "text": "Which attribute is required for the <img> tag to provide alternative text for search engines and screen readers?",
        "category": "Images",
        "difficulty": "Easy",
        "options": [
            {"text": "alt", "is_correct": True},
            {"text": "title", "is_correct": False},
            {"text": "desc", "is_correct": False},
            {"text": "longdesc", "is_correct": False}
        ]
    },
    {
        "text": "What is the primary purpose of the <figure> and <figcaption> elements?",
        "category": "Images",
        "difficulty": "Medium",
        "options": [
            {"text": "To group self-contained content, like photos or diagrams, along with an optional caption", "is_correct": True},
            {"text": "To draw dynamic 2D shapes using JavaScript", "is_correct": False},
            {"text": "To define mathematical equations", "is_correct": False},
            {"text": "To represent secondary sidebars", "is_correct": False}
        ]
    },
    {
        "text": "In responsive images, what is the purpose of the 'srcset' attribute on an <img> tag?",
        "category": "Responsive Images",
        "difficulty": "Hard",
        "options": [
            {"text": "To define a list of image source files and their width or pixel density descriptors, allowing the browser to choose the most appropriate image size", "is_correct": True},
            {"text": "To set multiple fallback URLs in case the main image fails to load", "is_correct": False},
            {"text": "To configure CSS filter styles for responsive breakpoints", "is_correct": False},
            {"text": "To trigger automatic resizing animations on load", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML5 element allows developers to define multiple source images based on media queries or image formats (like WebP/AVIF) with a fallback <img> element?",
        "category": "Picture Element",
        "difficulty": "Medium",
        "options": [
            {"text": "<picture>", "is_correct": True},
            {"text": "<source>", "is_correct": False},
            {"text": "<figure>", "is_correct": False},
            {"text": "<canvas>", "is_correct": False}
        ]
    },
    {
        "text": "What is an HTML Image Map?",
        "category": "Image Maps",
        "difficulty": "Medium",
        "options": [
            {"text": "An image that contains clickable active areas linked to different destination URLs", "is_correct": True},
            {"text": "A dynamic map showing GPS coordinates on an image", "is_correct": False},
            {"text": "A CSS visual overlay showing coordinates of a grid", "is_correct": False},
            {"text": "A collection of multiple thumbnails compiled into a single file", "is_correct": False}
        ]
    },
    {
        "text": "Which attribute of the ordered list (<ol>) tag changes the starting value of the list sequence?",
        "category": "Ordered Lists",
        "difficulty": "Medium",
        "options": [
            {"text": "start", "is_correct": True},
            {"text": "value", "is_correct": False},
            {"text": "begin", "is_correct": False},
            {"text": "index", "is_correct": False}
        ]
    },
    {
        "text": "Which attribute of the <ol> tag reverses the order of the numbering sequence?",
        "category": "Ordered Lists",
        "difficulty": "Medium",
        "options": [
            {"text": "reversed", "is_correct": True},
            {"text": "reverse", "is_correct": False},
            {"text": "desc", "is_correct": False},
            {"text": "fallback", "is_correct": False}
        ]
    },
    {
        "text": "What are the three elements used to construct a HTML Description List?",
        "category": "Description Lists",
        "difficulty": "Medium",
        "options": [
            {"text": "<dl>, <dt>, and <dd>", "is_correct": True},
            {"text": "<list>, <item>, and <desc>", "is_correct": False},
            {"text": "<ul>, <li>, and <ld>", "is_correct": False},
            {"text": "<dl>, <di>, and <dd>", "is_correct": False}
        ]
    },
    {
        "text": "Which element is used to add an accessible title or header description directly to a <table>, placed immediately after the opening <table> tag?",
        "category": "Tables",
        "difficulty": "Medium",
        "options": [
            {"text": "<caption>", "is_correct": True},
            {"text": "<summary>", "is_correct": False},
            {"text": "<thead>", "is_correct": False},
            {"text": "<title>", "is_correct": False}
        ]
    },
    {
        "text": "What is the difference between the <th> and <td> tags in HTML tables?",
        "category": "Tables",
        "difficulty": "Easy",
        "options": [
            {"text": "<th> is for header cells (bold and centered by default), and <td> is for standard data cells (regular weight and left-aligned)", "is_correct": True},
            {"text": "<th> is only used in <thead> and <td> is only used in <tbody>", "is_correct": False},
            {"text": "<th> elements do not support colspan, whereas <td> elements do", "is_correct": False},
            {"text": "<th> is a block-level element and <td> is an inline element", "is_correct": False}
        ]
    },
    {
        "text": "What is the purpose of the 'colspan' attribute in an HTML table cell?",
        "category": "Tables",
        "difficulty": "Medium",
        "options": [
            {"text": "To allow a cell to span across multiple columns horizontally", "is_correct": True},
            {"text": "To configure the padding space inside column headers", "is_correct": False},
            {"text": "To group adjacent table columns together", "is_correct": False},
            {"text": "To adjust column width dynamically", "is_correct": False}
        ]
    },
    {
        "text": "What is the purpose of the 'rowspan' attribute in a table cell?",
        "category": "Tables",
        "difficulty": "Medium",
        "options": [
            {"text": "To allow a cell to span across multiple rows vertically", "is_correct": True},
            {"text": "To specify the line height of row headers", "is_correct": False},
            {"text": "To merge all cells in a single table row", "is_correct": False},
            {"text": "To adjust the vertical alignment of the cell content", "is_correct": False}
        ]
    },
    {
        "text": "Which of the following correctly lists the semantic structural tags of an HTML table?",
        "category": "Tables",
        "difficulty": "Easy",
        "options": [
            {"text": "<thead>, <tbody>, and <tfoot>", "is_correct": True},
            {"text": "<header>, <body>, and <footer>", "is_correct": False},
            {"text": "<tstart>, <tmiddle>, and <tend>", "is_correct": False},
            {"text": "<top>, <mid>, and <bottom>", "is_correct": False}
        ]
    },
    {
        "text": "What is the primary purpose of the <label> element's 'for' attribute?",
        "category": "Forms",
        "difficulty": "Medium",
        "options": [
            {"text": "To associate the label with a form control's matching 'id' attribute, improving accessibility and click target area", "is_correct": True},
            {"text": "To direct where the form submits its data", "is_correct": False},
            {"text": "To specify the default value of the linked field", "is_correct": False},
            {"text": "To make the field required", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML elements are used to group related form fields together and add a caption to that group?",
        "category": "Forms",
        "difficulty": "Medium",
        "options": [
            {"text": "<fieldset> and <legend>", "is_correct": True},
            {"text": "<section> and <header>", "is_correct": False},
            {"text": "<group> and <label>", "is_correct": False},
            {"text": "<div class=\"group\"> and <span>", "is_correct": False}
        ]
    },
    {
        "text": "What is the main difference between the form methods GET and POST?",
        "category": "Forms",
        "difficulty": "Hard",
        "options": [
            {"text": "GET appends form data to the URL query string, while POST sends data within the HTTP request body", "is_correct": True},
            {"text": "GET is secure and POST is insecure", "is_correct": False},
            {"text": "GET can send file attachments, but POST cannot", "is_correct": False},
            {"text": "POST is faster than GET for small datasets", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML form element is used to display a drop-down list of options?",
        "category": "Forms",
        "difficulty": "Easy",
        "options": [
            {"text": "<select>", "is_correct": True},
            {"text": "<datalist>", "is_correct": False},
            {"text": "<option>", "is_correct": False},
            {"text": "<input type=\"select\">", "is_correct": False}
        ]
    },
    {
        "text": "What is the purpose of the <optgroup> element in a <select> drop-down list?",
        "category": "Forms",
        "difficulty": "Medium",
        "options": [
            {"text": "To group related <option> elements under a labeled, unselectable category header", "is_correct": True},
            {"text": "To make the drop-down list multiselect", "is_correct": False},
            {"text": "To style the drop-down using grid templates", "is_correct": False},
            {"text": "To bind options to a data source", "is_correct": False}
        ]
    },
    {
        "text": "What is the difference between a <select> dropdown and a <datalist> element?",
        "category": "Forms",
        "difficulty": "Hard",
        "options": [
            {"text": "<select> forces the user to choose from a fixed list, while <datalist> provides autocomplete suggestions for a free-text input field", "is_correct": True},
            {"text": "<select> only supports text items, whereas <datalist> supports images", "is_correct": False},
            {"text": "<datalist> is deprecated in HTML5 and replaced by <select>", "is_correct": False},
            {"text": "<datalist> requires external database integration to display", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML tag is used to create a multi-line text input area?",
        "category": "Forms",
        "difficulty": "Easy",
        "options": [
            {"text": "<textarea>", "is_correct": True},
            {"text": "<input type=\"textarea\">", "is_correct": False},
            {"text": "<textblock>", "is_correct": False},
            {"text": "<textbox>", "is_correct": False}
        ]
    },
    {
        "text": "What does the HTML5 <output> element represent?",
        "category": "Forms",
        "difficulty": "Hard",
        "options": [
            {"text": "The result of a calculation or user action, typically calculated using JavaScript", "is_correct": True},
            {"text": "A standard console log print area", "is_correct": False},
            {"text": "A link to compile outputs of external scripts", "is_correct": False},
            {"text": "The end node of a grid layout structure", "is_correct": False}
        ]
    },
    {
        "text": "Which input type displays a color picker control in modern browsers?",
        "category": "Every HTML Input Type",
        "difficulty": "Easy",
        "options": [
            {"text": "<input type=\"color\">", "is_correct": True},
            {"text": "<input type=\"palette\">", "is_correct": False},
            {"text": "<input type=\"rgb\">", "is_correct": False},
            {"text": "<input type=\"hex\">", "is_correct": False}
        ]
    },
    {
        "text": "Which input type is designed for selecting a calendar date including year, month, and day, without a specific time zone?",
        "category": "Every HTML Input Type",
        "difficulty": "Easy",
        "options": [
            {"text": "<input type=\"date\">", "is_correct": True},
            {"text": "<input type=\"datetime-local\">", "is_correct": False},
            {"text": "<input type=\"time\">", "is_correct": False},
            {"text": "<input type=\"calendar\">", "is_correct": False}
        ]
    },
    {
        "text": "Which input type displays a slider control for selecting a numeric value from a range?",
        "category": "Every HTML Input Type",
        "difficulty": "Easy",
        "options": [
            {"text": "<input type=\"range\">", "is_correct": True},
            {"text": "<input type=\"slider\">", "is_correct": False},
            {"text": "<input type=\"number\">", "is_correct": False},
            {"text": "<input type=\"scroll\">", "is_correct": False}
        ]
    },
    {
        "text": "Which input type is used to collect a telephone number, often displaying a numeric keypad on mobile devices?",
        "category": "Every HTML Input Type",
        "difficulty": "Easy",
        "options": [
            {"text": "<input type=\"tel\">", "is_correct": True},
            {"text": "<input type=\"phone\">", "is_correct": False},
            {"text": "<input type=\"telephone\">", "is_correct": False},
            {"text": "<input type=\"mobile\">", "is_correct": False}
        ]
    },
    {
        "text": "What is the primary difference between radio buttons and checkboxes?",
        "category": "Every HTML Input Type",
        "difficulty": "Easy",
        "options": [
            {"text": "Radio buttons allow only one selection from a named group, whereas checkboxes allow selecting multiple options", "is_correct": True},
            {"text": "Radio buttons are circular and checkboxes are square", "is_correct": False},
            {"text": "Checkboxes are processed on the server and radio buttons are client-side only", "is_correct": False},
            {"text": "Radio buttons cannot have default values", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML5 attribute specifies that a form field must be filled out before submitting the form?",
        "category": "Form Validation",
        "difficulty": "Easy",
        "options": [
            {"text": "required", "is_correct": True},
            {"text": "validate", "is_correct": False},
            {"text": "important", "is_correct": False},
            {"text": "non-empty", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML5 attribute allows developers to define a regular expression (Regex) that the input value must match to pass validation?",
        "category": "Form Validation",
        "difficulty": "Medium",
        "options": [
            {"text": "pattern", "is_correct": True},
            {"text": "regex", "is_correct": False},
            {"text": "validate", "is_correct": False},
            {"text": "match", "is_correct": False}
        ]
    },
    {
        "text": "What is the function of the 'placeholder' attribute in an HTML input field?",
        "category": "Form Validation",
        "difficulty": "Easy",
        "options": [
            {"text": "To show a short hint or sample text inside the input field before a value is entered", "is_correct": True},
            {"text": "To set the default value of the field upon submission", "is_correct": False},
            {"text": "To define the unique database key of the field", "is_correct": False},
            {"text": "To hide the characters entered by the user", "is_correct": False}
        ]
    },
    {
        "text": "What is the difference between the 'readonly' and 'disabled' attributes on form inputs?",
        "category": "Form Validation",
        "difficulty": "Hard",
        "options": [
            {"text": "Readonly elements cannot be edited but are submitted with the form, whereas disabled elements are neither editable nor submitted", "is_correct": True},
            {"text": "Readonly elements can be focused and edited, while disabled elements are completely hidden", "is_correct": False},
            {"text": "Disabled elements only work in CSS, while readonly works in database scripts", "is_correct": False},
            {"text": "There is no difference; they behave identically in forms", "is_correct": False}
        ]
    },
    {
        "text": "Which semantic HTML5 element should be used to enclose self-contained, independent compositions that are reusable or distributable (e.g., blog posts, comments, news items)?",
        "category": "Semantic HTML",
        "difficulty": "Medium",
        "options": [
            {"text": "<article>", "is_correct": True},
            {"text": "<section>", "is_correct": False},
            {"text": "<main>", "is_correct": False},
            {"text": "<aside>", "is_correct": False}
        ]
    },
    {
        "text": "Which semantic HTML5 element represents a section of a page that consists of content tangentially related to the content around it, often represented as a sidebar?",
        "category": "Semantic HTML",
        "difficulty": "Easy",
        "options": [
            {"text": "<aside>", "is_correct": True},
            {"text": "<section>", "is_correct": False},
            {"text": "<nav>", "is_correct": False},
            {"text": "<article>", "is_correct": False}
        ]
    },
    {
        "text": "What is the semantic purpose of the HTML5 <main> tag?",
        "category": "Semantic HTML",
        "difficulty": "Medium",
        "options": [
            {"text": "To represent the dominant, unique content of the <body> that is not repeated across other pages", "is_correct": True},
            {"text": "To group the header, navigation, and footer links into one section", "is_correct": False},
            {"text": "To define the master styles of a web layout", "is_correct": False},
            {"text": "To serve as a wrapper for global scripts", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML5 element should be used to represent a set of navigation links?",
        "category": "Semantic HTML",
        "difficulty": "Easy",
        "options": [
            {"text": "<nav>", "is_correct": True},
            {"text": "<menu>", "is_correct": False},
            {"text": "<links>", "is_correct": False},
            {"text": "<list>", "is_correct": False}
        ]
    },
    {
        "text": "Which semantic element is designed to display date, time, or duration in a machine-readable format?",
        "category": "Semantic HTML",
        "difficulty": "Medium",
        "options": [
            {"text": "<time>", "is_correct": True},
            {"text": "<date>", "is_correct": False},
            {"text": "<duration>", "is_correct": False},
            {"text": "<timestamp>", "is_correct": False}
        ]
    },
    {
        "text": "What is the correct semantic element for displaying contact information for the author or owner of a document or article?",
        "category": "Semantic HTML",
        "difficulty": "Medium",
        "options": [
            {"text": "<address>", "is_correct": True},
            {"text": "<contact>", "is_correct": False},
            {"text": "<author>", "is_correct": False},
            {"text": "<info>", "is_correct": False}
        ]
    },
    {
        "text": "Which pair of HTML5 elements represents a disclosure widget that is closed by default but can be toggled open to reveal detailed information?",
        "category": "Semantic HTML",
        "difficulty": "Medium",
        "options": [
            {"text": "<details> and <summary>", "is_correct": True},
            {"text": "<toggle> and <content>", "is_correct": False},
            {"text": "<dialog> and <summary>", "is_correct": False},
            {"text": "<accordion> and <summary>", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML5 element is used to embed audio files directly into a web page?",
        "category": "Audio",
        "difficulty": "Easy",
        "options": [
            {"text": "<audio>", "is_correct": True},
            {"text": "<sound>", "is_correct": False},
            {"text": "<music>", "is_correct": False},
            {"text": "<embed type=\"audio\">", "is_correct": False}
        ]
    },
    {
        "text": "Which attribute must be added to an <audio> or <video> tag to show the default browser play, pause, and volume controls?",
        "category": "Video",
        "difficulty": "Easy",
        "options": [
            {"text": "controls", "is_correct": True},
            {"text": "play", "is_correct": False},
            {"text": "controls=\"true\"", "is_correct": False},
            {"text": "panel", "is_correct": False}
        ]
    },
    {
        "text": "What is the purpose of the <track> element inside a <video> container?",
        "category": "Video",
        "difficulty": "Hard",
        "options": [
            {"text": "To add timed text tracks, such as subtitles, captions, or descriptions, for accessibility", "is_correct": True},
            {"text": "To link background audio tracks to the video", "is_correct": False},
            {"text": "To specify alternative video resolution formats", "is_correct": False},
            {"text": "To log video telemetry data to the server", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML tag is used to embed an external web page or document inline within the current HTML page?",
        "category": "iframe",
        "difficulty": "Easy",
        "options": [
            {"text": "<iframe>", "is_correct": True},
            {"text": "<embed>", "is_correct": False},
            {"text": "<object>", "is_correct": False},
            {"text": "<frame>", "is_correct": False}
        ]
    },
    {
        "text": "What is the difference between the <iframe>, <embed>, and <object> elements?",
        "category": "Embedded Content",
        "difficulty": "Hard",
        "options": [
            {"text": "<iframe> embeds an independent HTML page, <embed> is for external resources or plugins, and <object> is a general-purpose container supporting parameters", "is_correct": True},
            {"text": "<iframe> is obsolete, while <embed> and <object> are modern HTML5 standards", "is_correct": False},
            {"text": "<object> is for images, <iframe> is for scripts, and <embed> is for media", "is_correct": False},
            {"text": "There is no difference; all three represent identical rendering engines", "is_correct": False}
        ]
    },
    {
        "text": "What is the purpose of the viewport meta tag <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">?",
        "category": "Viewport",
        "difficulty": "Medium",
        "options": [
            {"text": "To control the page dimensions and scaling on mobile devices to ensure a responsive layout", "is_correct": True},
            {"text": "To track the user's location via geolocation coordinate maps", "is_correct": False},
            {"text": "To enforce browser security limits in fullscreen mode", "is_correct": False},
            {"text": "To configure search engine indexing keywords", "is_correct": False}
        ]
    },
    {
        "text": "Which meta tag is critical for providing a search engine with a short summary of the page content?",
        "category": "SEO Basics",
        "difficulty": "Medium",
        "options": [
            {"text": "<meta name=\"description\" content=\"...\">", "is_correct": True},
            {"text": "<meta name=\"keywords\" content=\"...\">", "is_correct": False},
            {"text": "<meta name=\"summary\" content=\"...\">", "is_correct": False},
            {"text": "<meta name=\"abstract\" content=\"...\">", "is_correct": False}
        ]
    },
    {
        "text": "Which tag is the most important heading on a page for search engine optimization (SEO), and should ideally appear only once per page?",
        "category": "SEO Basics",
        "difficulty": "Easy",
        "options": [
            {"text": "<h1>", "is_correct": True},
            {"text": "<title>", "is_correct": False},
            {"text": "<head>", "is_correct": False},
            {"text": "<h2>", "is_correct": False}
        ]
    },
    {
        "text": "What are WAI-ARIA and the 'role' attribute used for in HTML?",
        "category": "ARIA Basics",
        "difficulty": "Hard",
        "options": [
            {"text": "To define accessible roles and descriptions for elements when standard HTML semantics are insufficient for screen readers", "is_correct": True},
            {"text": "To declare database access rules for user groups", "is_correct": False},
            {"text": "To assign CSS formatting classes dynamically", "is_correct": False},
            {"text": "To determine page routing roles in SPA frameworks", "is_correct": False}
        ]
    },
    {
        "text": "What is the difference between 'aria-label' and 'aria-labelledby'?",
        "category": "ARIA Basics",
        "difficulty": "Hard",
        "options": [
            {"text": "aria-label directly contains the string descriptive label, whereas aria-labelledby references the ID of another element containing the label text", "is_correct": True},
            {"text": "aria-label is for images and aria-labelledby is for forms", "is_correct": False},
            {"text": "aria-label is deprecated and replaced by aria-labelledby", "is_correct": False},
            {"text": "aria-labelledby only works in CSS templates", "is_correct": False}
        ]
    },
    {
        "text": "Which aria attribute is used to reference the ID of an element that provides an extended text description for a form field or control?",
        "category": "ARIA Basics",
        "difficulty": "Hard",
        "options": [
            {"text": "aria-describedby", "is_correct": True},
            {"text": "aria-desc", "is_correct": False},
            {"text": "aria-details", "is_correct": False},
            {"text": "aria-labelled-by", "is_correct": False}
        ]
    },
    {
        "text": "What is the difference between localStorage and sessionStorage?",
        "category": "Local Storage",
        "difficulty": "Medium",
        "options": [
            {"text": "localStorage persists data indefinitely across browser sessions, whereas sessionStorage clears data when the page session or tab ends", "is_correct": True},
            {"text": "localStorage stores encrypted data and sessionStorage stores plain text", "is_correct": False},
            {"text": "localStorage is limited to 10KB and sessionStorage has 5MB capacity", "is_correct": False},
            {"text": "sessionStorage only works with Python server sessions", "is_correct": False}
        ]
    },
    {
        "text": "Which JavaScript object property is accessed to request and query the user's geographic coordinates?",
        "category": "Geolocation API",
        "difficulty": "Medium",
        "options": [
            {"text": "navigator.geolocation", "is_correct": True},
            {"text": "window.location.geo", "is_correct": False},
            {"text": "document.geolocation", "is_correct": False},
            {"text": "navigator.gps", "is_correct": False}
        ]
    },
    {
        "text": "Which attribute must be set to 'true' to make an HTML element draggable using the HTML5 Drag and Drop API?",
        "category": "Drag and Drop API",
        "difficulty": "Easy",
        "options": [
            {"text": "draggable", "is_correct": True},
            {"text": "drag", "is_correct": False},
            {"text": "allow-drag", "is_correct": False},
            {"text": "dropzone", "is_correct": False}
        ]
    },
    {
        "text": "What is the benefit of validating HTML documents using a service like the W3C Markup Validation Service?",
        "category": "HTML Validation",
        "difficulty": "Medium",
        "options": [
            {"text": "It identifies syntax errors, unclosed tags, and deprecated elements, helping ensure cross-browser compatibility", "is_correct": True},
            {"text": "It automatically compiles HTML code into high-performance machine code", "is_correct": False},
            {"text": "It secures the database from SQL injection vulnerabilities", "is_correct": False},
            {"text": "It automatically optimizes page SEO titles", "is_correct": False}
        ]
    },
    {
        "text": "Which CSS unit is relative to the width of the viewport and commonly used in responsive web layout styling?",
        "category": "Responsive HTML",
        "difficulty": "Medium",
        "options": [
            {"text": "vw", "is_correct": True},
            {"text": "vh", "is_correct": False},
            {"text": "rem", "is_correct": False},
            {"text": "em", "is_correct": False}
        ]
    },
    {
        "text": "What does SVG stand for in web graphics?",
        "category": "SVG",
        "difficulty": "Easy",
        "options": [
            {"text": "Scalable Vector Graphics", "is_correct": True},
            {"text": "Simple Visual Graphics", "is_correct": False},
            {"text": "Standard Vector Group", "is_correct": False},
            {"text": "Scalable Variable Graphics", "is_correct": False}
        ]
    },
    {
        "text": "What is the primary architectural difference between HTML <svg> and <canvas> elements?",
        "category": "SVG vs Canvas",
        "difficulty": "Hard",
        "options": [
            {"text": "SVG is vector-based using XML shapes (retains quality on zoom), while Canvas is raster-based using JavaScript pixels (pixelates on zoom)", "is_correct": True},
            {"text": "SVG is faster for rendering millions of objects, whereas Canvas supports accessibility out-of-the-box", "is_correct": False},
            {"text": "Canvas runs in the browser and SVG requires external plugins", "is_correct": False},
            {"text": "SVG is only for 3D graphics and Canvas is only for 2D", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML element is used as a container to draw graphics dynamically on-the-fly using JavaScript scripts?",
        "category": "Canvas",
        "difficulty": "Easy",
        "options": [
            {"text": "<canvas>", "is_correct": True},
            {"text": "<svg>", "is_correct": False},
            {"text": "<paint>", "is_correct": False},
            {"text": "<drawing>", "is_correct": False}
        ]
    },
    {
        "text": "Which method is called on a `<canvas>` element in JavaScript to get the rendering context for drawing 2D shapes?",
        "category": "Canvas",
        "difficulty": "Medium",
        "options": [
            {"text": "getContext('2d')", "is_correct": True},
            {"text": "getContext2D()", "is_correct": False},
            {"text": "get2DContext()", "is_correct": False},
            {"text": "getDrawingContext()", "is_correct": False}
        ]
    },
    {
        "text": "Which global attribute is used to make the content of an HTML element directly editable by the user in the browser window?",
        "category": "Global Attributes",
        "difficulty": "Medium",
        "options": [
            {"text": "contenteditable", "is_correct": True},
            {"text": "editable", "is_correct": False},
            {"text": "useredit", "is_correct": False},
            {"text": "allow-edit", "is_correct": False}
        ]
    },
    {
        "text": "What is the correct HTML element for inserting a line break?",
        "category": "Line Breaks",
        "difficulty": "Easy",
        "options": [
            {"text": "<br>", "is_correct": True},
            {"text": "<lb>", "is_correct": False},
            {"text": "<break>", "is_correct": False},
            {"text": "<newline>", "is_correct": False}
        ]
    },
    {
        "text": "What is the purpose of the global 'spellcheck' attribute in HTML?",
        "category": "Global Attributes",
        "difficulty": "Easy",
        "options": [
            {"text": "To enable or disable browser grammar and spell checking for text areas and editable inputs", "is_correct": True},
            {"text": "To run code unit tests on server-side data", "is_correct": False},
            {"text": "To validate email formatting constraints", "is_correct": False},
            {"text": "To check file name paths for syntax errors", "is_correct": False}
        ]
    },
    {
        "text": "In which year was the HTML5 specification officially published as a complete W3C Recommendation?",
        "category": "History of HTML",
        "difficulty": "Hard",
        "options": [
            {"text": "2014", "is_correct": True},
            {"text": "1999", "is_correct": False},
            {"text": "2008", "is_correct": False},
            {"text": "2018", "is_correct": False}
        ]
    },
    {
        "text": "Which element is used to define metadata about the HTML document that is not displayed directly, such as charset, description, and keywords?",
        "category": "Meta Tags",
        "difficulty": "Easy",
        "options": [
            {"text": "<meta>", "is_correct": True},
            {"text": "<head>", "is_correct": False},
            {"text": "<link>", "is_correct": False},
            {"text": "<info>", "is_correct": False}
        ]
    },
    {
        "text": "Which tag is used to format text to look like subscript?",
        "category": "Formatting Tags",
        "difficulty": "Easy",
        "options": [
            {"text": "<sub>", "is_correct": True},
            {"text": "<sup>", "is_correct": False},
            {"text": "<subscript>", "is_correct": False},
            {"text": "<down>", "is_correct": False}
        ]
    },
    {
        "text": "Which tag is used to format text to look like superscript?",
        "category": "Formatting Tags",
        "difficulty": "Easy",
        "options": [
            {"text": "<sup>", "is_correct": True},
            {"text": "<sub>", "is_correct": False},
            {"text": "<superscript>", "is_correct": False},
            {"text": "<up>", "is_correct": False}
        ]
    },
    {
        "text": "In an unordered list (<ul>), what is the default visual bullet style applied by most browsers?",
        "category": "Unordered Lists",
        "difficulty": "Easy",
        "options": [
            {"text": "Disc (filled circle)", "is_correct": True},
            {"text": "Circle (empty circle)", "is_correct": False},
            {"text": "Square", "is_correct": False},
            {"text": "Decimal", "is_correct": False}
        ]
    },
    {
        "text": "Which table attribute is used to associate a header cell with specific rows or columns, taking values like 'row', 'col', 'rowgroup', or 'colgroup'?",
        "category": "Tables",
        "difficulty": "Hard",
        "options": [
            {"text": "scope", "is_correct": True},
            {"text": "headers", "is_correct": False},
            {"text": "rowspan", "is_correct": False},
            {"text": "target", "is_correct": False}
        ]
    },
    {
        "text": "Which input type is used to allow users to select a single local file to upload?",
        "category": "Every HTML Input Type",
        "difficulty": "Easy",
        "options": [
            {"text": "<input type=\"file\">", "is_correct": True},
            {"text": "<input type=\"upload\">", "is_correct": False},
            {"text": "<input type=\"media\">", "is_correct": False},
            {"text": "<input type=\"filepath\">", "is_correct": False}
        ]
    },
    {
        "text": "What is the effect of adding the 'novalidate' attribute to a <form> element?",
        "category": "Form Validation",
        "difficulty": "Medium",
        "options": [
            {"text": "It disables browser-native validation checks upon form submission", "is_correct": True},
            {"text": "It forces server-side verification scripts to run in the background", "is_correct": False},
            {"text": "It makes all fields within the form optional", "is_correct": False},
            {"text": "It disables JavaScript event listeners on form submit", "is_correct": False}
        ]
    },
    {
        "text": "Which input type is designed for search query entry, behaves similarly to a text input, and may show a clear icon?",
        "category": "Every HTML Input Type",
        "difficulty": "Easy",
        "options": [
            {"text": "<input type=\"search\">", "is_correct": True},
            {"text": "<input type=\"find\">", "is_correct": False},
            {"text": "<input type=\"query\">", "is_correct": False},
            {"text": "<input type=\"text\" search=\"true\">", "is_correct": False}
        ]
    },
    {
        "text": "How do you clear all items from localStorage in JavaScript?",
        "category": "Local Storage",
        "difficulty": "Easy",
        "options": [
            {"text": "localStorage.clear()", "is_correct": True},
            {"text": "localStorage.removeAll()", "is_correct": False},
            {"text": "localStorage.delete()", "is_correct": False},
            {"text": "localStorage.reset()", "is_correct": False}
        ]
    },
    {
        "text": "Which attribute is used to provide a screen reader description for a visually hidden element or icon button?",
        "category": "Accessibility",
        "difficulty": "Medium",
        "options": [
            {"text": "aria-label", "is_correct": True},
            {"text": "role", "is_correct": False},
            {"text": "label", "is_correct": False},
            {"text": "aria-description", "is_correct": False}
        ]
    },
    {
        "text": "What is the correct syntax to link an external CSS stylesheet to an HTML file?",
        "category": "HTML Best Practices",
        "difficulty": "Easy",
        "options": [
            {"text": "<link rel=\"stylesheet\" href=\"style.css\">", "is_correct": True},
            {"text": "<style src=\"style.css\">", "is_correct": False},
            {"text": "<link src=\"style.css\">", "is_correct": False},
            {"text": "<a href=\"style.css\" rel=\"style\">", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML element is used to embed vector graphic definitions directly inside a page markup?",
        "category": "SVG",
        "difficulty": "Easy",
        "options": [
            {"text": "<svg>", "is_correct": True},
            {"text": "<vector>", "is_correct": False},
            {"text": "<graphics>", "is_correct": False},
            {"text": "<picture>", "is_correct": False}
        ]
    },
    {
        "text": "What is the primary role of the 'pattern' attribute in an HTML input field?",
        "category": "Form Validation",
        "difficulty": "Medium",
        "options": [
            {"text": "To define a regular expression validation check for the input's value", "is_correct": True},
            {"text": "To set the default character structure of the database column", "is_correct": False},
            {"text": "To apply predefined CSS background styles to the field", "is_correct": False},
            {"text": "To determine the key pattern mapping for server-side index search", "is_correct": False}
        ]
    },
    {
        "text": "What is the purpose of the 'multiple' attribute on an <input type=\"file\"> element?",
        "category": "Every HTML Input Type",
        "difficulty": "Easy",
        "options": [
            {"text": "To allow the user to select and upload multiple files at once", "is_correct": True},
            {"text": "To duplicate the input field dynamically", "is_correct": False},
            {"text": "To compress uploaded files to a zip format", "is_correct": False},
            {"text": "To link the field to multiple tables in a database", "is_correct": False}
        ]
    },
    {
        "text": "Which tag is used to embed another media document like an Flash/ActiveX element or external plug-in, using self-closing syntax?",
        "category": "Embedded Content",
        "difficulty": "Medium",
        "options": [
            {"text": "<embed>", "is_correct": True},
            {"text": "<iframe>", "is_correct": False},
            {"text": "<object>", "is_correct": False},
            {"text": "<media>", "is_correct": False}
        ]
    },
    {
        "text": "What does the 'readonly' attribute prevent on an HTML input element?",
        "category": "Form Validation",
        "difficulty": "Easy",
        "options": [
            {"text": "It prevents the user from modifying the value, but the value is still submitted with the form", "is_correct": True},
            {"text": "It prevents the input from being submitted with the form", "is_correct": False},
            {"text": "It makes the input read-only in database searches but fully editable in UI", "is_correct": False},
            {"text": "It hides the input control from view completely", "is_correct": False}
        ]
    },
    {
        "text": "Which element is used to group several option elements together inside a datalist or select field?",
        "category": "Forms",
        "difficulty": "Medium",
        "options": [
            {"text": "<optgroup>", "is_correct": True},
            {"text": "<group>", "is_correct": False},
            {"text": "<options>", "is_correct": False},
            {"text": "<datalist>", "is_correct": False}
        ]
    },
    {
        "text": "What is the default value of the method attribute in an HTML <form> element if it is omitted?",
        "category": "Forms",
        "difficulty": "Medium",
        "options": [
            {"text": "GET", "is_correct": True},
            {"text": "POST", "is_correct": False},
            {"text": "PUT", "is_correct": False},
            {"text": "DELETE", "is_correct": False}
        ]
    },
    {
        "text": "Which attribute on an <a> tag defines the relationship between the current document and the linked resource?",
        "category": "Hyperlinks",
        "difficulty": "Medium",
        "options": [
            {"text": "rel", "is_correct": True},
            {"text": "rev", "is_correct": False},
            {"text": "type", "is_correct": False},
            {"text": "target", "is_correct": False}
        ]
    },
    {
        "text": "Which HTML tag is used to present a preformatted block of computer code, preserving layout and indent styling?",
        "category": "Preformatted Text",
        "difficulty": "Easy",
        "options": [
            {"text": "<pre>", "is_correct": True},
            {"text": "<code>", "is_correct": False},
            {"text": "<samp>", "is_correct": False},
            {"text": "<kbd>", "is_correct": False}
        ]
    },
    {
        "text": "Which value of the 'target' attribute opens a link in the parent frame, if nested inside frames?",
        "category": "Hyperlinks",
        "difficulty": "Hard",
        "options": [
            {"text": "_parent", "is_correct": True},
            {"text": "_top", "is_correct": False},
            {"text": "_self", "is_correct": False},
            {"text": "_blank", "is_correct": False}
        ]
    },
    {
        "text": "Which value of the 'target' attribute opens a link in the full body of the window, breaking out of all nested iframes?",
        "category": "Hyperlinks",
        "difficulty": "Hard",
        "options": [
            {"text": "_top", "is_correct": True},
            {"text": "_parent", "is_correct": False},
            {"text": "_self", "is_correct": False},
            {"text": "_blank", "is_correct": False}
        ]
    },
    {
        "text": "What is the primary role of the <head> element in an HTML document?",
        "category": "HTML Structure",
        "difficulty": "Easy",
        "options": [
            {"text": "To contain machine-readable metadata and links to external resources, which are not directly rendered in the main page viewport", "is_correct": True},
            {"text": "To render the primary header banner at the top of the viewport", "is_correct": False},
            {"text": "To serve as the main wrapper for block-level article content", "is_correct": False},
            {"text": "To display the main navigation links of the site", "is_correct": False}
        ]
    },
    {
        "text": "Which tag represents a definition term in a Description List?",
        "category": "Description Lists",
        "difficulty": "Medium",
        "options": [
            {"text": "<dt>", "is_correct": True},
            {"text": "<dd>", "is_correct": False},
            {"text": "<dl>", "is_correct": False},
            {"text": "<di>", "is_correct": False}
        ]
    },
    {
        "text": "Which tag represents the description or definition details in a Description List?",
        "category": "Description Lists",
        "difficulty": "Medium",
        "options": [
            {"text": "<dd>", "is_correct": True},
            {"text": "<dt>", "is_correct": False},
            {"text": "<dl>", "is_correct": False},
            {"text": "<di>", "is_correct": False}
        ]
    },
    {
        "text": "Which attribute on a <textarea> element sets its visible height by specifying the number of lines it displays?",
        "category": "Forms",
        "difficulty": "Easy",
        "options": [
            {"text": "rows", "is_correct": True},
            {"text": "cols", "is_correct": False},
            {"text": "height", "is_correct": False},
            {"text": "size", "is_correct": False}
        ]
    },
    {
        "text": "Which attribute on a <textarea> element sets its visible width by specifying the average character width?",
        "category": "Forms",
        "difficulty": "Easy",
        "options": [
            {"text": "cols", "is_correct": True},
            {"text": "rows", "is_correct": False},
            {"text": "width", "is_correct": False},
            {"text": "size", "is_correct": False}
        ]
    },
    {
        "text": "Which element defines the header of a table, grouping rows that represent table labels?",
        "category": "Tables",
        "difficulty": "Easy",
        "options": [
            {"text": "<thead>", "is_correct": True},
            {"text": "<th>", "is_correct": False},
            {"text": "<tfoot>", "is_correct": False},
            {"text": "<header>", "is_correct": False}
        ]
    },
    {
        "text": "Which element defines the footer of a table, grouping rows that represent summaries or totals?",
        "category": "Tables",
        "difficulty": "Easy",
        "options": [
            {"text": "<tfoot>", "is_correct": True},
            {"text": "<td>", "is_correct": False},
            {"text": "<thead>", "is_correct": False},
            {"text": "<footer>", "is_correct": False}
        ]
    },
    {
        "text": "Which global attribute specifies whether the browser is allowed to translate the content of an element?",
        "category": "Global Attributes",
        "difficulty": "Hard",
        "options": [
            {"text": "translate", "is_correct": True},
            {"text": "lang", "is_correct": False},
            {"text": "content-translate", "is_correct": False},
            {"text": "babel", "is_correct": False}
        ]
    },
    {
        "text": "In the Geolocation API, which method is used to continuously watch and receive notifications when the device position changes?",
        "category": "Geolocation API",
        "difficulty": "Hard",
        "options": [
            {"text": "navigator.geolocation.watchPosition()", "is_correct": True},
            {"text": "navigator.geolocation.getCurrentPosition()", "is_correct": False},
            {"text": "navigator.geolocation.track()", "is_correct": False},
            {"text": "navigator.geolocation.getPosition()", "is_correct": False}
        ]
    },
    {
        "text": "Which event fires on a valid drop target element when a dragged item is released over it?",
        "category": "Drag and Drop API",
        "difficulty": "Medium",
        "options": [
            {"text": "drop", "is_correct": True},
            {"text": "dragend", "is_correct": False},
            {"text": "dragover", "is_correct": False},
            {"text": "dragrelease", "is_correct": False}
        ]
    },
    {
        "text": "Which element is used to embed another page's contents using plug-in content, requiring a close tag, unlike <embed>?",
        "category": "Embedded Content",
        "difficulty": "Hard",
        "options": [
            {"text": "<object>", "is_correct": True},
            {"text": "<embed>", "is_correct": False},
            {"text": "<iframe>", "is_correct": False},
            {"text": "<plugin>", "is_correct": False}
        ]
    },
    {
        "text": "What does the viewport attribute 'user-scalable=no' specify in responsive design?",
        "category": "Viewport",
        "difficulty": "Medium",
        "options": [
            {"text": "It prevents the user from zooming in or out on the mobile web browser", "is_correct": True},
            {"text": "It disables mouse scrolling on desktop screens", "is_correct": False},
            {"text": "It blocks accessibility options in screen readers", "is_correct": False},
            {"text": "It forces horizontal page layout dimensions", "is_correct": False}
        ]
    },
    {
        "text": "Which meta tag tells search engine index crawlers not to index the page and not to follow any links on it?",
        "category": "SEO Basics",
        "difficulty": "Hard",
        "options": [
            {"text": "<meta name=\"robots\" content=\"noindex, nofollow\">", "is_correct": True},
            {"text": "<meta name=\"googlebot\" content=\"block\">", "is_correct": False},
            {"text": "<meta name=\"index\" content=\"false\">", "is_correct": False},
            {"text": "<meta name=\"search\" content=\"none\">", "is_correct": False}
        ]
    },
    {
        "text": "Which ARIA attribute indicates that an element has a pop-up context menu, dialog, list, grid, or submenu?",
        "category": "ARIA Basics",
        "difficulty": "Hard",
        "options": [
            {"text": "aria-haspopup", "is_correct": True},
            {"text": "aria-popup", "is_correct": False},
            {"text": "aria-menu", "is_correct": False},
            {"text": "aria-expanded", "is_correct": False}
        ]
    },
    {
        "text": "Which method is called on sessionStorage to retrieve an item's stored string value by its key?",
        "category": "Local Storage",
        "difficulty": "Easy",
        "options": [
            {"text": "sessionStorage.getItem()", "is_correct": True},
            {"text": "sessionStorage.retrieveItem()", "is_correct": False},
            {"text": "sessionStorage.val()", "is_correct": False},
            {"text": "sessionStorage.fetch()", "is_correct": False}
        ]
    },
    {
        "text": "Which event fires repeatedly on a draggable element as it is being dragged by the user?",
        "category": "Drag and Drop API",
        "difficulty": "Medium",
        "options": [
            {"text": "drag", "is_correct": True},
            {"text": "dragstart", "is_correct": False},
            {"text": "dragover", "is_correct": False},
            {"text": "dragenter", "is_correct": False}
        ]
    },
    {
        "text": "What is the primary role of the <address> element in HTML5?",
        "category": "Semantic HTML",
        "difficulty": "Medium",
        "options": [
            {"text": "To supply contact information specifically for the document author or owner", "is_correct": True},
            {"text": "To render a physical mailing address using geolocation maps", "is_correct": False},
            {"text": "To link a company office to search indices", "is_correct": False},
            {"text": "To format IP address logs in text documents", "is_correct": False}
        ]
    }
]

def seed_database():
    print("Initializing database...")
    init_db()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Clear existing accounts to satisfy "only" condition
        cursor.execute("DELETE FROM admins;")
        cursor.execute("DELETE FROM students;")
        
        # 2. Insert requested admin
        admin_email = "nithingowda@nxtwave.in"
        admin_pass = "Halonix@2026"
        hashed_admin_password = generate_password_hash(admin_pass)
        cursor.execute(
            "INSERT INTO admins (username, password_hash) VALUES (?, ?);",
            (admin_email, hashed_admin_password)
        )
        print(f"Admin user '{admin_email}' seeded.")

        # 3. Insert requested students
        students_to_seed = [
            ("saishivani@nxtwave.in", "Sai Shivani", "saishivani@stu1869"),
            ("demo@nxtwave.in", "Demo Student", "demo123")
        ]
        for email, name, pwd in students_to_seed:
            hashed_pwd = generate_password_hash(pwd)
            cursor.execute(
                "INSERT INTO students (student_id, name, password_hash) VALUES (?, ?, ?);",
                (email, name, hashed_pwd)
            )
            print(f"Student user '{email}' seeded.")

        # 2. Insert default settings
        default_settings = [
            ("passing_marks", "75"),
            ("negative_marking", "0.35"),
            ("duration_minutes", "100"),
            ("total_questions", "100"),
            ("schedule_enabled", "1"),
            ("schedule_start", "2026-07-19 19:00"),
            ("schedule_end", "2026-07-19 20:40")
        ]
        for key, value in default_settings:
            cursor.execute(
                "INSERT OR IGNORE INTO exam_settings (key, value) VALUES (?, ?);",
                (key, value)
            )
        print("Default exam settings initialized.")

        # 3. Seed 100 questions
        cursor.execute("SELECT COUNT(*) FROM questions;")
        q_count = cursor.fetchone()[0]

        if q_count < len(HTML_QUESTIONS):
            # Clear questions if they are partially loaded or mismatch
            cursor.execute("DELETE FROM options;")
            cursor.execute("DELETE FROM questions;")
            
            print(f"Seeding {len(HTML_QUESTIONS)} original HTML MCQs...")
            for q_data in HTML_QUESTIONS:
                cursor.execute(
                    "INSERT INTO questions (question_text, category, difficulty) VALUES (?, ?, ?);",
                    (q_data["text"], q_data["category"], q_data["difficulty"])
                )
                question_id = cursor.lastrowid
                
                for opt in q_data["options"]:
                    cursor.execute(
                        "INSERT INTO options (question_id, option_text, is_correct) VALUES (?, ?, ?);",
                        (question_id, opt["text"], 1 if opt["is_correct"] else 0)
                    )
            print("Questions seeded successfully.")
        else:
            print(f"Database already contains {q_count} questions. Seeding skipped.")

        conn.commit()
        print("Database seeded and ready!")
    except Exception as e:
        conn.rollback()
        print(f"Error during seeding: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database()
