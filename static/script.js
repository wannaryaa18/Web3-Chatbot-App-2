document.addEventListener('DOMContentLoaded', function() {
  const textInput = document.getElementById('textInput');
  const sendButton = document.getElementById('sendButton');
  const chatbox = document.getElementById('chatbox');

  function sendMessage() {
    const userMessage = textInput.value.trim();

    if (userMessage === "") return;

    appendMessage(userMessage, 'user-message');

    textInput.value = '';

    setTimeout(() => {
      fetch('/get_response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      })
      .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
      })
      .then(data => {
        appendMessage(data.response, 'bot-message');
      })
      .catch(error => {
        console.error('Error:', error);
        appendMessage('Maaf, terjadi kesalahan saat memproses permintaan Anda.', 'bot-message');
      });
    }, 300);
  }

  function appendMessage(message, senderClass) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', senderClass);

    const avatarElement = document.createElement('div');
    avatarElement.classList.add('avatar');

    if (senderClass === 'bot-message') {
      avatarElement.textContent = '🤖';
    } else if (senderClass === 'user-message') {
      avatarElement.textContent = '😎';
    }

    const messageContentElement = document.createElement('div');
    messageContentElement.classList.add('message-content');

    const messageBubble = document.createElement('div');
    messageBubble.classList.add('message-bubble');
    messageBubble.textContent = message;

    messageContentElement.appendChild(messageBubble);

    messageElement.appendChild(avatarElement);
    messageElement.appendChild(messageContentElement);

    chatbox.appendChild(messageElement);

    chatbox.scrollTo({
      top: chatbox.scrollHeight,
      behavior: 'smooth'
    });
  }

  sendButton.addEventListener('click', sendMessage);

  textInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });
});
