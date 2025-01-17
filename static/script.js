document.getElementById('generateSessionBtn').addEventListener('click', function () {
    const generateSessionBtn = document.getElementById('generateSessionBtn');

    // Check if the element is disabled
    if (generateSessionBtn.disabled) {
        return; // Exit the function if the element is disabled
    }
    const xhr = new XMLHttpRequest();
    document.getElementById('result').innerHTML = `
          <p>Generating session... Do not click the above button again. This might take a few minutes.</p>
      `;
    document.getElementById("generateSessionBtn").disabled = true;
    xhr.open('POST', '/create_container', true);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  
    xhr.onload = function () {
      if (xhr.status >= 200 && xhr.status < 300) {
        const response = JSON.parse(xhr.responseText);
        document.getElementById("generateSessionBtn").disabled = false;
        displayResult(response);
        refreshContainers();
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
        html += `
              <li>
    <h3>Session Details:</h3>
    <p><strong>Name:</strong> ${container.name}</p>
    <p><strong>Username:</strong> ${container.username}</p>
    <p><strong>Password:</strong> ${container.password}</p>
    <p><strong>Hostname:</strong> ${container.hostname}</p>
    <p><strong>Port:</strong> ${container.port}</p>
    <div class="button-container">
      <button id="delete-btn-${container.name}" class="delete-btn">Delete</button>
      <button class="connect-btn" id="connect-btn-${container.name}">Connect</button>
    </div>
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
            html += `
              <li>
    <h3>Session Details:</h3>
    <p><strong>Name:</strong> ${container.name}</p>
    <p><strong>Username:</strong> ${container.username}</p>
    <p><strong>Password:</strong> ${container.password}</p>
    <p><strong>Hostname:</strong> ${container.hostname}</p>
    <p><strong>Port:</strong> ${container.port}</p>
    <div class="button-container">
      <button id="delete-btn-${container.name}" class="delete-btn">Delete</button>
      <button class="connect-btn" id="connect-btn-${container.name}">Connect</button>
    </div>
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

  function refreshContainers() {
    fetch('/get_user_containers')
      .then(response => response.json())
      .then(data => {
        const containersDiv = document.getElementById('containers');
        if (data.length > 0) {
          let html = '<ul class="container-list">';
          data.forEach(container => {
            html += `
              <li>
    <h3>Session Details:</h3>
    <p><strong>Name:</strong> ${container.name}</p>
    <p><strong>Username:</strong> ${container.username}</p>
    <p><strong>Password:</strong> ${container.password}</p>
    <p><strong>Hostname:</strong> ${container.hostname}</p>
    <p><strong>Port:</strong> ${container.port}</p>
    <div class="button-container">
      <button id="delete-btn-${container.name}" class="delete-btn">Delete</button>
      <button id="restart-btn-${container.name}" class="restart-btn">Restart</button>
      <button class="connect-btn" id="connect-btn-${container.name}">Connect</button>
    </div>
  </li>`;
          });
          html += '</ul>';
          containersDiv.innerHTML = html;
  
          // Add event listeners to buttons
          const deleteBtns = document.getElementsByClassName('delete-btn');
          for (let i = 0; i < deleteBtns.length; i++) {
            deleteBtns[i].addEventListener('click', function () {
              const containerId = this.id.split('-')[2];
              deleteContainer(containerId);
            });
          }
          const restartBtns = document.getElementsByClassName('restart-btn');
          for (let i = 0; i < deleteBtns.length; i++) {
            restartBtns[i].addEventListener('click', function () {
              const containerId = this.id.split('-')[2];
              restartContainer(containerId);
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
  };
  
  function deleteContainer(containerId) {
    if (confirm('Are you sure you want to delete this container?')) {
      fetch(`/delete_container?id=${containerId}`, { method: 'DELETE' })
        .then(response => {
          if (response.ok) {
            refreshContainers();
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

  function restartContainer(containerId) {
    if (confirm('Are you sure you want to restart this container?')) {
      fetch(`/container/restart?id=${containerId}`, { method: 'POST' })
        .then(response => {
          if (response.ok) {
            refreshContainers();
          } else {
            console.error('Error restarting container:', response.statusText);
            alert('Error restarting container. Please try again.');
          }
        })
        .catch(error => {
          console.error('Error restarting container:', error);
          alert('Error restarting container. Please try again.');
        });
    }
  }
document.getElementById('logoutButton').addEventListener('click', function () {

    // Redirect users to the logout page
    window.location.href = '/logout';
});

// Get the popup and close button
var popup = document.getElementById("connectionPopup");
var closePopup = document.getElementsByClassName("close-popup")[0];

// Function to open the connection details popup
function openConnectionPopup(containerId) {
    // Fetch connection details based on the container ID
    fetch(`/get_connection_details?id=${containerId}`)
        .then(response => response.json())
        .then(data => {
            // Populate the popup with connection details
            document.getElementById('connectionDetails').innerHTML = `
                <strong>Name:</strong> ${data.name}<br>
                <strong>Username:</strong> ${data.username}<br>
                <strong>Password:</strong> ${data.password}<br>
                <strong>Hostname:</strong> ${data.hostname}<br>
                <strong>Port:</strong> ${data.port}<br>
                <strong>SSH Command:</strong> <code>${data.ssh_command}</code>
            `;
            // Show the popup
            popup.style.display = "block";
        })
        .catch(error => {
            console.error('Error fetching connection details:', error);
            document.getElementById('connectionDetails').innerHTML = '<p>Error fetching connection details.</p>';
            popup.style.display = "block"; // Show popup even if there's an error
        });
}

// Event listener for dynamically created connect buttons
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('connect-btn')) {
        const containerId = event.target.id.split('-')[2]; // Get container ID from button ID
        openConnectionPopup(containerId); // Open new connection details popup
    }
});

// When the user clicks on <span> (x), close the popup
closePopup.onclick = function() {
    popup.style.display = "none";
}

// When the user clicks anywhere outside of the popup, close it
window.onclick = function(event) {
    if (event.target == popup) {
        popup.style.display = "none";
    }
};