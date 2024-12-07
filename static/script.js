document.getElementById('generateSessionBtn').addEventListener('click', function () {
    const xhr = new XMLHttpRequest();
    document.getElementById('result').innerHTML = `
          <p>Generating session... Do not click the above button again. This might take a few minutes.</p>
      `;
    xhr.open('POST', '/create_container', true);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  
    xhr.onload = function () {
      if (xhr.status >= 200 && xhr.status < 300) {
        const response = JSON.parse(xhr.responseText);
        displayResult(response);
      } else {
        console.error('Error:', xhr.responseText);
        document.getElementById('result').innerHTML = '<p>Error generating session. Please try again.</p>';
      }
    };
  
    xhr.onerror = function () {
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
  
    // Update the containers div with the user's containers
    const containersDiv = document.getElementById('containers');
    const containers = JSON.parse(data.containers);
    if (containers.length > 0) {
      let html = '<ul class="container-list">';
      containers.forEach(container => {
        html += `<li>
                  <strong>Name:</strong> ${container.name}, <strong>Username:</strong> ${container.username}, <strong>Port:</strong> ${container.port}, <strong>Password:</strong> ${container.password},
                  <button id="delete-btn-${container.id}" class="delete-btn">Delete</button>
                </li>`;
      });
      html += '</ul>';
      containersDiv.innerHTML = html;
  
      // Add event listeners to delete buttons
      const deleteBtns = document.getElementsByClassName('delete-btn');
      for (let i = 0; i < deleteBtns.length; i++) {
        deleteBtns[i].addEventListener('click', function () {
          const containerId = this.id.split('-')[2];
          deleteContainer(containerId);
        });
      }
    } else {
      containersDiv.innerHTML = '<p>No containers assigned.</p>';
    }
  }
  
  document.addEventListener('DOMContentLoaded', function () {
    // Load the user's containers on page load
    fetch('/get_user_containers')
      .then(response => response.json())
      .then(data => {
        const containersDiv = document.getElementById('containers');
        if (data.length > 0) {
          let html = '<ul class="container-list">';
          data.forEach(container => {
            html += `<li>
                      <strong>Name:</strong> ${container.name}, <strong>Username:</strong> ${container.username}, <strong>Port:</strong> ${container.port}, <strong>Password:</strong> ${container.password},
                      <button id="delete-btn-${container.name}" class="delete-btn">Delete</button>
                    </li>`;
            const containernametodelete = container.name;
          });
          html += '</ul>';
          containersDiv.innerHTML = html;
  
          // Add event listeners to delete buttons
          const deleteBtns = document.getElementsByClassName('delete-btn');
          for (let i = 0; i < deleteBtns.length; i++) {
            deleteBtns[i].addEventListener('click', function () {
              const containerId = this.id.split('-')[2];
              deleteContainer(containerId);
            });
          }
        } else {
          containersDiv.innerHTML = '<p>No containers assigned.</p>';
        }
      })
      .catch(error => {
        console.error('Error fetching containers:', error);
        document.getElementById('containers').innerHTML = '<p>Error fetching containers. Please try again.</p>';
      });
  });
  
  function deleteContainer(containerId) {
    if (confirm('Are you sure you want to delete this container?')) {
      fetch(`/delete_container?id=${containerId}`, { method: 'DELETE' })
        .then(response => {
          if (response.ok) {
            displayResult({ containers: JSON.stringify([]) });
          } else {
            console.error('Error deleting container:', response.statusText);
            alert('Error deleting container. Please try again.');
          }
        })
        .catch(error => {
          console.error('Error deleting container:', error);
          alert('Error deleting container. Please try again.');
        });
    }
  }
document.getElementById('logoutButton').addEventListener('click', function () {

    // Redirect users to the logout page
    window.location.href = '/logout';
});