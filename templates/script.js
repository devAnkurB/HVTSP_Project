const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB
const chatBox = document.getElementById("chatBox");
const uploadForm = document.getElementById("uploadForm");
const fileInput = document.getElementById("excelFileInput");
const questionInput = document.getElementById("userQuestionInput");
const loadingScreen = document.getElementById("loadingScreen");

const fileTooltip = document.getElementById("fileTooltip");
const textTooltip = document.getElementById("textTooltip");

// Format bytes to human readable string
function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// Append user text message (right side)
function appendUserMessage(text) {
  const wrapper = document.createElement("div");
  wrapper.className = "message user-message";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  wrapper.appendChild(bubble);
  chatBox.appendChild(wrapper);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Append AI message (left side)
function appendAIMessage(text) {
  const wrapper = document.createElement("div");
  wrapper.className = "message ai-message";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  wrapper.appendChild(bubble);
  chatBox.appendChild(wrapper);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Append error message centered with red background
function appendErrorMessage(text) {
  const wrapper = document.createElement("div");
  wrapper.className = "message error-message";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  wrapper.appendChild(bubble);
  chatBox.appendChild(wrapper);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Append file message as user message (right side), clickable for download
function appendFileMessage(file) {
  const wrapper = document.createElement("div");
  wrapper.className = "message file-message user-message";

  const link = document.createElement("a");
  link.className = "file-attachment";
  link.href = URL.createObjectURL(file);
  link.download = file.name;
  link.title = `Download ${file.name}`;
  link.rel = "noopener noreferrer";

  const iconSpan = document.createElement("span");
  iconSpan.className = "file-icon";
  iconSpan.textContent = "📄";

  const detailsDiv = document.createElement("div");
  detailsDiv.className = "file-details";

  const nameSpan = document.createElement("span");
  nameSpan.className = "file-name";
  nameSpan.textContent = file.name;

  const sizeSpan = document.createElement("span");
  sizeSpan.className = "file-size";
  sizeSpan.textContent = formatFileSize(file.size);

  detailsDiv.appendChild(nameSpan);
  detailsDiv.appendChild(sizeSpan);

  link.appendChild(iconSpan);
  link.appendChild(detailsDiv);
  wrapper.appendChild(link);
  chatBox.appendChild(wrapper);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Show tooltip at mouse position
function showTooltip(e, tooltip) {
  tooltip.style.display = "block";
  tooltip.style.left = e.clientX + 15 + "px";
  tooltip.style.top = e.clientY + 15 + "px";
}

// Hide tooltip
function hideTooltip(tooltip) {
  tooltip.style.display = "none";
}

// Tooltip event listeners
const uploadLabel = document.querySelector(".upload-icon");
if (uploadLabel && fileTooltip) {
  uploadLabel.addEventListener("mousemove", (e) => showTooltip(e, fileTooltip));
  uploadLabel.addEventListener("mouseleave", () => hideTooltip(fileTooltip));
}

if (questionInput && textTooltip) {
  questionInput.addEventListener("mousemove", (e) =>
    showTooltip(e, textTooltip)
  );
  questionInput.addEventListener("mouseleave", () => hideTooltip(textTooltip));
}

// Form submit handler
uploadForm.addEventListener("submit", (e) => {
  e.preventDefault();

  // Clear previous warnings/errors (you can extend to add warnings if needed)

  // Validate file
  if (fileInput.files.length === 0) {
    appendErrorMessage("Please upload a file.");
    return;
  }
  const file = fileInput.files[0];
  if (file.size > MAX_FILE_SIZE) {
    appendErrorMessage("File is too large. Maximum allowed size is 10 MB.");
    return;
  }

  // Validate question
  const question = questionInput.value.trim();
  if (!question) {
    appendErrorMessage("Please enter a question.");
    return;
  }

  // Append user messages: file + question
  appendFileMessage(file);
  appendUserMessage(question);

  // Show loading only if a file is uploaded
  loadingScreen.style.display = "flex";

  // Simulate API call or form submission here...
  // For demo: hide loading after 3 seconds and append a dummy AI response
  setTimeout(() => {
    loadingScreen.style.display = "none";
    appendAIMessage(
      "This is a dummy AI response based on your uploaded file and question."
    );
    // Clear question input but keep file selected
    questionInput.value = "";
  }, 3000);
});
