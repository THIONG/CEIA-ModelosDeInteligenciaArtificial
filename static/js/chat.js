(function() {
    'use strict';
    const textarea = document.getElementById("messageInput");
    const placeholderLabel = document.querySelector(".placeholder-label");
    const chatBox = document.getElementById("chatBox");
    const minHeight = 50;
    const API_URL = window.location.origin;
    let currentMaxHeight = minHeight;

    function init() {
        setupTextareaHandlers();
    }

    function setupTextareaHandlers() {
        textarea.style.height = minHeight + "px";
        textarea.style.lineHeight = "50px";
        textarea.addEventListener("input", handleTextareaInput);
        textarea.addEventListener("blur", handleTextareaBlur);
        textarea.addEventListener("keypress", handleTextareaKeypress);
    }

    function handleTextareaInput() {
        if (this.value.trim() === "") {
            this.classList.add("empty");
        } else {
            this.classList.remove("empty");
        }
        this.style.height = minHeight + "px";
        const newHeight = this.scrollHeight;
        if (newHeight > currentMaxHeight) {
            currentMaxHeight = newHeight;
            this.style.height = newHeight + "px";
        } else {
            this.style.height = currentMaxHeight + "px";
        }
        placeholderLabel.style.opacity = this.value ? "0" : "1";
    }

    function handleTextareaBlur() {
        if (!this.value.trim()) {
            currentMaxHeight = minHeight;
            this.style.height = minHeight + "px";
            this.style.lineHeight = "50px";
            placeholderLabel.style.opacity = "1";
            this.classList.add("empty");
        }
    }

    function handleTextareaKeypress(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    }

    async function sendMessage() {
        const messageText = textarea.value.trim();
        if (!messageText) return;
        addUserMessage(messageText);
        const thinkingMessage = addThinkingMessage();
        resetTextarea();
        try {
            const data = await sendMessageToServer(messageText);
            thinkingMessage.remove();
            addBotMessage(data.reply);
        } catch (error) {
            console.error("Error:", error);
            thinkingMessage.remove();
            addErrorMessage();
        }
        scrollToBottom();
    }

    function addUserMessage(messageText) {
        const userMessage = document.createElement("div");
        userMessage.className = "message user-message";
        let formattedUserMessage = messageText;
        formattedUserMessage = formatCodeBlocks(formattedUserMessage);
        userMessage.innerHTML = DOMPurify.sanitize(marked.parse(formattedUserMessage));
        setupCopyButtons(userMessage);
        Prism.highlightAllUnder(userMessage);
        chatBox.appendChild(userMessage);
    }

    function addThinkingMessage() {
        const thinkingMessage = document.createElement("div");
        thinkingMessage.className = "message bot-message thinking-message";
        thinkingMessage.innerHTML = `
            <div class="spinner"></div>
            <span>Chuma está pensando...</span>
        `;
        chatBox.appendChild(thinkingMessage);
        return thinkingMessage;
    }

    function addBotMessage(reply) {
        const botMessage = document.createElement("div");
        botMessage.className = "message bot-message";
        const thinkRegex = /<think>([\s\S]*?)<\/think>/gi;
        let thinkContent = "";
        const cleanReply = reply.replace(thinkRegex, (match, content) => {
            thinkContent += DOMPurify.sanitize(marked.parse(content));
            return "";
        });
        const formattedReply = formatCodeBlocks(cleanReply);
        botMessage.innerHTML = DOMPurify.sanitize(marked.parse(formattedReply));
        if (thinkContent) {
            addReasoningToggle(botMessage, thinkContent);
        }
        setupCopyButtons(botMessage);
        Prism.highlightAllUnder(botMessage);
        chatBox.appendChild(botMessage);
    }

    function addReasoningToggle(messageElement, content) {
        const thinkContainer = document.createElement("div");
        thinkContainer.innerHTML = `
            <button class="reasoning-toggle">▼ Mostrar razonamiento</button>
            <div class="reasoning-content">${content}</div>
        `;
        messageElement.appendChild(thinkContainer);
        const toggleBtn = thinkContainer.querySelector(".reasoning-toggle");
        const contentDiv = thinkContainer.querySelector(".reasoning-content");
        toggleBtn.addEventListener("click", () => {
            contentDiv.classList.toggle("expanded");
            toggleBtn.textContent = contentDiv.classList.contains("expanded")
                ? "▲ Ocultar razonamiento"
                : "▼ Mostrar razonamiento";
        });
    }

    function addErrorMessage() {
        const errorMessage = document.createElement("div");
        errorMessage.className = "message bot-message";
        errorMessage.textContent = "Error al obtener respuesta. Intenta de nuevo.";
        chatBox.appendChild(errorMessage);
    }

    function formatCodeBlocks(text) {
        const codeRegex = /```(\w+)?\s*([\s\S]*?)```/gi;
        return text.replace(
            codeRegex,
            (match, lang, code) => `
                <pre>
                    <div class="code-header">
                        <span class="language-label">${(lang || 'text').toUpperCase()}</span>
                        <button class="copy-button">Copiar</button>
                    </div>
                    <code class="language-${lang || 'text'}">${DOMPurify.sanitize(code)}</code>
                </pre>`
        );
    }

    function setupCopyButtons(element) {
        element.querySelectorAll(".copy-button").forEach((copyBtn) => {
            copyBtn.onclick = () => {
                const codeContent = copyBtn.closest("pre").querySelector("code").textContent;
                navigator.clipboard.writeText(codeContent).then(() => {
                    copyBtn.textContent = "¡Copiado!";
                    setTimeout(() => (copyBtn.textContent = "Copiar"), 2000);
                });
            };
        });
    }

    async function sendMessageToServer(messageText) {
        const response = await fetch(`${API_URL}/get-response`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: messageText }),
        });
        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }
        return await response.json();
    }

    function resetTextarea() {
        textarea.value = "";
        placeholderLabel.style.opacity = "1";
        currentMaxHeight = minHeight;
        textarea.style.height = minHeight + "px";
        textarea.style.lineHeight = "50px";
        textarea.classList.add("empty");
    }

    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    window.clearChat = async function() {
        try {
            const response = await fetch(`${API_URL}/reset`, {
                method: "POST",
                headers: { "Content-Type": "application/json" }
            });
            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }
            const data = await response.json();
            chatBox.innerHTML = "";
            const resetMessage = document.createElement("div");
            resetMessage.className = "message bot-message";
            resetMessage.textContent = "Chat reiniciado.";
            chatBox.appendChild(resetMessage);
        } catch (error) {
            console.error("Error al reiniciar el chat:", error);
            alert("Error al reiniciar el chat.");
        }
    };
    document.addEventListener('DOMContentLoaded', init);
})();