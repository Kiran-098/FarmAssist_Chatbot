document.getElementById('send-button').addEventListener('click', handleUserInput);
document.getElementById('user-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleUserInput();
    }
});

function handleUserInput() {
    const userMessage = document.getElementById('user-input').value.trim();
    if (userMessage) {
        appendMessage(userMessage, 'user');
        fetch('/ask', {  // Changed from '/get_response' to '/ask'
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: userMessage })
        })
        .then(response => response.json())
        .then(data => {
            appendMessage(data.response, 'bot');
        })
        .catch(error => console.error('Error:', error));
        document.getElementById('user-input').value = '';
    }
}

function appendMessage(message, sender) {
    const chatbox = document.getElementById('chatbox');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message', sender + '-message');
    messageDiv.innerHTML = `<p>${message}</p>`;
    chatbox.appendChild(messageDiv);
    chatbox.scrollTop = chatbox.scrollHeight;  // Scroll to the bottom
}
// Existing chatbot functionality remains unchanged

// Weather application functionality
document.getElementById('getWeather').addEventListener('click', function() {
    var city = document.getElementById('city').value;
    fetch('http://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&appid=cc2015775821e92628b22dbdaea835ae')
        .then(response => response.json())
        .then(data => {
            document.getElementById('temp').innerText = 'Temperature: ' + data.main.temp + '°C';
            document.getElementById('humid').innerText = 'Humidity: ' + data.main.humidity + '%';
            document.getElementById('cloud').innerText = 'Clouds: ' + data.clouds.all + '%';
            document.getElementById('wind').innerText = 'Wind Speed: ' + data.wind.speed + ' m/s';
        })
        .catch(error => console.error('Error:', error));
});

