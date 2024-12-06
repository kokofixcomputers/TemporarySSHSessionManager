document.getElementById('generateSessionBtn').addEventListener('click', function() {
    const xhr = new XMLHttpRequest();
    document.getElementById('result').innerHTML = `
        <p>Generating session... Do not click the above button again. This might take a few minutes.</p>
    `;
    xhr.open('POST', '/create_container', true);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');

    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
            const response = JSON.parse(xhr.responseText);
            displayResult(response);
        } else {
            console.error('Error:', xhr.responseText);
            document.getElementById('result').innerHTML = '<p>Error generating session. Please try again.</p>';
        }
    };

    xhr.onerror = function() {
        console.error('Request failed');
        document.getElementById('result').innerHTML = '<p>Request failed. Please check your connection.</p>';
    };

    xhr.send(JSON.stringify({})); // Send an empty object or any required params
});

function displayResult(data) {
    document.getElementById('result').innerHTML = `
        <h3>Session Details:</h3>
        <p><strong>Name:</strong> ${data.name}</p>
        <p><strong>Username:</strong> ${data.username}</p>
        <p><strong>Password:</strong> ${data.password}</p>
        <p><strong>Hostname:</strong> ${data.hostname}</p>
        <p><strong>Port:</strong> ${data.port}</p>
        <p><strong>SSH Command:</strong> <code>${data.ssh_command}</code></p>
    `;
}
