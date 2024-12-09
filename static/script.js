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
          <p><strong>Port:</strong> ${container.port}</p></li>
          <button id="delete-btn-${container.name}" class="delete-btn">Delete</button><button class="connect-btn" id="connect-btn-${container.name}">Connect</button>`;
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
          <p><strong>Port:</strong> ${container.port}</p></li>
          <button id="delete-btn-${container.name}" class="delete-btn">Delete</button><button class="connect-btn" id="connect-btn-${container.name}">Connect</button>`;
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
          <p><strong>Port:</strong> ${container.port}</p></li>
          <button id="delete-btn-${container.name}" class="delete-btn">Delete</button><button class="connect-btn" id="connect-btn-${container.name}">Connect</button>`;
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
document.getElementById('logoutButton').addEventListener('click', function () {

    // Redirect users to the logout page
    window.location.href = '/logout';
});

// Get the modal and close button
var modal = document.getElementById("myModal");
var span = document.getElementsByClassName("close")[0];

// Function to open modal and fetch connection details
// Function to open a new connection details container
function openConnectionDetails(containerId) {
  // Fetch connection details based on the container ID
  fetch(`/get_connection_details?id=${containerId}`)
      .then(response => response.json())
      .then(data => {
          // Create a new div for connection details
          const detailContainer = document.createElement('div');
          detailContainer.className = 'connection-detail'; // Add a class for styling
          
          // Populate the new container with connection details
          detailContainer.innerHTML = `
              <h3>Connection Details for ${data.name}</h3>
              <p><strong>Username:</strong> ${data.username}</p>
              <p><strong>Password:</strong> ${data.password}</p>
              <p><strong>Hostname:</strong> ${data.hostname}</p>
              <p><strong>Port:</strong> ${data.port}</p>
              <p><strong>SSH Command:</strong> <code>${data.ssh_command}</code></p>
              <button class="close-detail-btn">Close</button>
          `;

          // Append the new container to the main containers div
          document.getElementById('containers').appendChild(detailContainer);

          // Add event listener to close button
          detailContainer.querySelector('.close-detail-btn').addEventListener('click', function() {
              detailContainer.remove(); // Remove the detail container when closed
          });
      })
      .catch(error => {
          console.error('Error fetching connection details:', error);
          alert('Error fetching connection details.');
      });
}

// Event listener for dynamically created connect buttons
document.addEventListener('click', function(event) {
  if (event.target.classList.contains('connect-btn')) {
      const containerId = event.target.id.split('-')[2]; // Get container ID from button ID
      openConnectionDetails(containerId); // Open new connection details container
  }
});

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
};