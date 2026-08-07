const chatForm = document.querySelector("#chat-form");
const messageInput = document.querySelector("#message-input");
const messages = document.querySelector("#messages");

function addMessage(author, text, messageType) {
    const message = document.createElement("article");
    message.classList.add("message", `message-${messageType}`);

    const label = document.createElement("span");
    label.classList.add("message-label");
    label.textContent = author;

    const content = document.createElement("p");
    content.textContent = text;

    message.append(label, content);
    messages.append(message);
    messages.scrollTop = messages.scrollHeight;
}

function handleSubmit(event) {
    event.preventDefault();

    const text = messageInput.value.trim();

    if (!text) {
        return;
    }

    addMessage("You", text, "user");
    messageInput.value = "";

    addMessage(
        "System",
        "The browser interface works. The backend WebSocket is not connected yet.",
        "system",
    );
}

chatForm.addEventListener("submit", handleSubmit);