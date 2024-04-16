const chatbotIcon = document.getElementById("chatbot-icon");
const chatWindow = document.getElementById("chat-window");

// Global variable to track the most recent bot message
let lastBotMessage = null;

function toggleChatWindow() {
  chatWindow.classList.toggle("open");
  if (chatWindow.style.display === "none") {
    chatWindow.style.display = "block";
  } else {
    chatWindow.style.display = "none";
  }
}

// Toggle chat window visibility when the chatbot icon is clicked
chatbotIcon.addEventListener("click", toggleChatWindow);

function addMessageIntoChatWindow(sender, message, userQuery, isFeedbackRequiredForThisResponse) {
  var chatbox = document.getElementById("chatbox");
  var newMessage = document.createElement("div");
  newMessage.classList.add("chatbot-message");

  var messageContent = "<p>" + message + "</p>";
  var iconClass = sender === "You" ? "user-icon" : "bot-icon";
  var messageClass = sender === "You" ? "user-message" : "bot-message";
  var iconUrl =
    sender === "You"
      ? "{% static 'chatbotapp/images/user_icon.png' %}"
      : "{% static 'chatbotapp/images/chatbot.png' %}";

  removeUserFeedback();

  if (sender === "You") {
    newMessage.innerHTML = `
            <div class="message-container ${messageClass} user">
                <div class="message-content">${messageContent}</div>
            </div>
        `;
  } else {
    newMessage.innerHTML = `
            <div class="message-container ${messageClass}">
                <div class="message-content">${messageContent}</div>
            </div>
        `;

    // Update lastBotMessage when displaying a bot message
    lastBotMessage = newMessage;
  }

  if (isFeedbackRequiredForThisResponse === "Yes" ) {
    lastBotMessage.innerHTML += `
            <div class="user-feedback">
                <div class="thumbs-up-icon" onclick="feedback('like','${userQuery}', '${message}')">
                  <svg viewBox="0 0 24 24" width="20"><path d="M14.99 3H6c-.8 0-1.52.48-1.83 1.21L.91 11.82C.06 13.8 1.51 16 3.66 16h5.65l-.95 4.58c-.1.5.05 1.01.41 1.37.29.29.67.43 1.05.43s.77-.15 1.06-.44l5.53-5.54c.37-.37.58-.88.58-1.41V5c0-1.1-.9-2-2-2m-4.33 16.33.61-2.92.5-2.41H3.66c-.47 0-.72-.28-.83-.45-.11-.17-.27-.51-.08-.95L6 5h8.99v9.99zM21 3c-1.1 0-2 .9-2 2v8c0 1.1.9 2 2 2s2-.9 2-2V5c0-1.1-.9-2-2-2"></path></svg>
                </div>
                <div class="thumbs-down-icon" onclick="feedback('dislike', '${userQuery}', '${message}')">
                  <svg class="thumbs-down-icon" viewBox="0 0 24 24" width="20"><path d="M14.99 3H6c-.8 0-1.52.48-1.83 1.21L.91 11.82C.06 13.8 1.51 16 3.66 16h5.65l-.95 4.58c-.1.5.05 1.01.41 1.37.29.29.67.43 1.05.43s.77-.15 1.06-.44l5.53-5.54c.37-.37.58-.88.58-1.41V5c0-1.1-.9-2-2-2m-4.33 16.33.61-2.92.5-2.41H3.66c-.47 0-.72-.28-.83-.45-.11-.17-.27-.51-.08-.95L6 5h8.99v9.99zM21 3c-1.1 0-2 .9-2 2v8c0 1.1.9 2 2 2s2-.9 2-2V5c0-1.1-.9-2-2-2"></path></svg>
                </div>
            </div>
        `;
  }

  chatbox.appendChild(newMessage);
  chatbox.scrollTop = chatbox.scrollHeight;
}

// for removing previous feedback
function removeUserFeedback() {
  if (lastBotMessage) {
    const userFeedback = lastBotMessage.querySelector(".user-feedback");
    if (userFeedback) {
      userFeedback.remove();
    }
  }
}

//adding the initial message by bot
addMessageIntoChatWindow( "Bot", "Hello User, How can I help you?", "", "No");

function processInput() {
  var input = document.getElementById("input");
  var userQuery = input.value;
  var userFeedbackForLastResponse="";

  //  adding user query to the chat window
  addMessageIntoChatWindow("You", userQuery, userQuery, "No");

  $.get("/chatbot", {
    userQuery: userQuery,
    userFeedback: userFeedbackForLastResponse,
    botResponse: "",
  }).done(function (data) {
//   adding the response given by bot in the chat window
    addMessageIntoChatWindow("Bot", data["response"], userQuery, data["isUserFeedbackRequiredForThisResponse"]);
  });

  input.value = "";
}

document.getElementById("input").addEventListener("keydown", function (e) {
  if (e.keyCode === 13) {
    processInput();
  }
});

function feedback(userFeedbackForLastResponse, userQuery, botResponse) {
//  console.log("In feedback function");

      // sending feedback to the backend with the original user query and bot response and getting feedback response
      $.get("/chatbot", {
        userQuery: userQuery,
        userFeedback: userFeedbackForLastResponse,
        botResponse: botResponse,
      }).done(function (data) {
//        adding feedback response from the bot in chat window
        addMessageIntoChatWindow("Bot", data["response"], userQuery, data["isUserFeedbackRequiredForThisResponse"]);
      });

}
