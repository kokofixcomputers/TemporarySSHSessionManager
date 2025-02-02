document.getElementById('generate_key').addEventListener('click', function () {
    const xhr = new XMLHttpRequest();
    document.getElementById("generate_key").disabled = true;
    xhr.open('POST', '/apikey/generate', true);

    xhr.onload = function () {
      if (xhr.status >= 200 && xhr.status < 300) {
        document.getElementById('messages').innerHTML = xhr.responseText;
        fetchApiKeys(); // Fetch updated list of API keys after generation
      } else {
        console.error('Error:', xhr.responseText);
        document.getElementById('messages').innerHTML = '<p>Error Generating API-KEY</p>';
      }
    };

    xhr.onerror = function () {
      console.error('Request failed');
      document.getElementById('messages').innerHTML = '<p>Request failed. Please check your connection.</p>';
    };

    xhr.send();
});

document.getElementById('logoutButton').addEventListener('click', function () {
    window.location.href = '/logout';
});

// Function to fetch and display API keys
// Function to fetch and display API keys
function fetchApiKeys() {
    fetch('/apikey/get')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // Expecting an array of strings
        })
        .then(data => {
            const tableBody = document.querySelector('#apiKeysTable tbody');
            tableBody.innerHTML = ''; // Clear existing rows

            data.forEach(apiKey => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${apiKey}</td>
                    <td><button class="redbutton delete-button" data-api-key="${apiKey}">Delete</button></td>
                `;
                tableBody.appendChild(row);
            });

            // Add event listeners for delete buttons
            document.querySelectorAll('.delete-button').forEach(button => {
                button.addEventListener('click', function() {
                    const apiKeyToDelete = this.getAttribute('data-api-key');
                    deleteApiKey(apiKeyToDelete);
                });
            });
        })
        .catch(error => {
            console.error('Error fetching API keys:', error);
            document.getElementById('messages').innerHTML = '<p>Error fetching API keys.</p>';
        });
}

// Function to delete an API key
function deleteApiKey(apiKey) {
    fetch('/apikey/delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ api_key: apiKey })
    })
    .then(response => response.text())
    .then(message => {
        document.getElementById('messages').innerHTML = `<p>${message}</p>`;
        fetchApiKeys(); // Refresh the list of API keys after deletion
    })
    .catch(error => {
        console.error('Error deleting API key:', error);
        document.getElementById('messages').innerHTML = '<p>Error deleting API key.</p>';
    });
}


// Initial fetch of API keys when the page loads
fetchApiKeys();
