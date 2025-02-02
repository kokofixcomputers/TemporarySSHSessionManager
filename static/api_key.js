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
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching API keys:', error);
            document.getElementById('messages').innerHTML = '<p>Error fetching API keys.</p>';
        });
}

// Initial fetch of API keys when the page loads
fetchApiKeys();
