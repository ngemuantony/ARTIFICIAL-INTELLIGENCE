document.addEventListener("DOMContentLoaded", function () {
    var conversationItems = document.querySelectorAll(".previous-conversations li");
    conversationItems.forEach(function (item) {
        item.addEventListener("click", function () {
            var userInput = this.textContent.trim();
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/get_bot_response", true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    var botResponse = response.response;
                    displayConversation(userInput, botResponse);
                    if (response.prompt_correction) {
                        document.getElementById('updateBotKnowledge').style.display = 'block';
                        document.getElementById('userInputToUpdate').value = userInput;
                        document.getElementById('correctInput').value = '';
                    } else {
                        document.getElementById('updateBotKnowledge').style.display = 'none';
                    }
                }
            };
            xhr.send(JSON.stringify({ user_input: userInput }));
        });
    });
});

function displayConversation(userInput, botResponse) {
    var chatbox = document.getElementById("chatbox");
    chatbox.innerHTML = "";

    var userMessage = document.createElement("p");
    userMessage.classList.add("user-message");
    userMessage.textContent = "You: " + userInput;
    chatbox.appendChild(userMessage);

    var botMessage = document.createElement("p");
    botMessage.classList.add("bot-message");
    botMessage.textContent = "CyberLinkBot: " + botResponse;
    chatbox.appendChild(botMessage);
}

function sendMessage() {
    var userInput = document.getElementById("userInput").value.trim();
    if (userInput === "") return;

    var chatbox = document.getElementById("chatbox");
    var userMessage = document.createElement("p");
    userMessage.classList.add("user-message");
    userMessage.textContent = "You: " + userInput;
    chatbox.appendChild(userMessage);

    var processingMessage = document.createElement("p");
    processingMessage.classList.add("processing");
    processingMessage.textContent = "Processing...";
    chatbox.appendChild(processingMessage);

    var userInputTextarea = document.getElementById("userInput");
    userInputTextarea.disabled = true;
    var sendButton = document.getElementById("sendButton");

    if (sendButton) {
        sendButton.textContent = "Processing...";
        sendButton.disabled = true; // Disable the send button during processing
    }

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/get_bot_response", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            chatbox.removeChild(processingMessage);
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                var botResponse = response.response;
                var botMessage = document.createElement("p");
                botMessage.classList.add("bot-message");
                botMessage.textContent = "CyberLinkBot: " + botResponse;
                chatbox.appendChild(botMessage);
                chatbox.scrollTop = chatbox.scrollHeight;

                if (response.prompt_correction) {
                    document.getElementById('updateBotKnowledge').style.display = 'block';
                    document.getElementById('userInputToUpdate').value = userInput;
                    document.getElementById('correctInput').value = '';
                } else {
                    document.getElementById('updateBotKnowledge').style.display = 'none';
                }
            } else {
                alert("An error occurred. Please try again later.");
            }

            userInputTextarea.disabled = false;
            if (sendButton) {
                sendButton.textContent = "Send";
                sendButton.disabled = false; // Re-enable the send button after processing
            }
        }
    };
    xhr.send(JSON.stringify({ user_input: userInput }));

    document.getElementById("userInput").value = "";
}

function updateBotKnowledge() {
    var userInputToUpdate = document.getElementById("userInputToUpdate").value.trim();
    var correctInput = document.getElementById("correctInput").value.trim();
    if (correctInput === "") return;

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/update_knowledge", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            alert("Bot knowledge updated successfully!");
            document.getElementById("correctInput").value = "";  // Reset the correct input field
            document.getElementById("updateBotKnowledge").style.display = "none";  // Hide the update knowledge section
            document.getElementById("sendButton").textContent = "Send";  // Reset the send button text
        }
    };
    xhr.send(JSON.stringify({ user_input: userInputToUpdate, correct_response: correctInput }));
}

function toggleBackgroundColor() {
    var body = document.body;
    var currentColor = body.style.backgroundColor;
    if (currentColor === "white" || currentColor === "") {
        body.style.backgroundColor = "black";
    } else if (currentColor === "black") {
        body.style.backgroundColor = "red";
    } else if (currentColor === "red") {
        body.style.backgroundColor = "gray";
    } else if (currentColor === "gray") {
        body.style.backgroundColor = "orange";
    } else if (currentColor === "orange") {
        body.style.backgroundColor = "white";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("userInput").addEventListener("keydown", function (event) {
        if (event.keyCode === 13 && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
});
