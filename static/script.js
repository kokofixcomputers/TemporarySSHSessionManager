// Declare modal and span variables globally
var modal;
var span;
var modal_create;
var span_create;
var modal_delete;
var span_delete;
var modal_connection;
var span_connection;
var tooltipContainer;
var tooltipContent;

// Function to open the modal
function openModal() {
    if (modal) {
        modal.style.display = "block";
    }
}
function openModalCreate() {
    if (modal_create) {
        modal_create.style.display = "block";
    }
}
function openModalDelete() {
    if (modal_delete) {
        modal_delete.style.display = "block";
    }
}
function openModalConnection() {
    if (modal_connection) {
        modal_connection.style.display = "block";
    }
}

// Function to close the modal
function closeModal() {
    if (modal) {
        modal.style.display = "none";
    }
}
function closeModalCreate() {
    if (modal_create) {
        modal_create.style.display = "none";
    }
}
function closeModalDelete() {
    if (modal_delete) {
        modal_delete.style.display = "none";
    }
}
function closeModalConnection() {
    if (modal_connection) {
        modal_connection.style.display = "none";
    }
}

// Wait for DOM content to load
document.addEventListener("DOMContentLoaded", function() {
    modal = document.getElementById("myModal");
    span = document.getElementsByClassName("close")[0];

    // Close the modal when the close button is clicked
    span.onclick = closeModal;

    // Close the modal when clicking outside of it
    window.onclick = function(event) {
        if (event.target == modal) {
            closeModal();
        }
    }
});
document.addEventListener("DOMContentLoaded", function() {
    modal_create = document.getElementById("myModalCreate");
    span_create = document.getElementsByClassName("close")[0];
    // Close the modal when the close button is clicked
    span_create.onclick = closeModalCreate;
    // Close the modal when clicking outside of it
    window.onclick = function(event) {
        if (event.target == modal_create) {
            closeModalCreate();
        }
    }
});
document.addEventListener("DOMContentLoaded", function() {
    modal_delete = document.getElementById("myModalDelete");
    span_delete = document.getElementsByClassName("close")[0];
    // Close the modal when the close button is clicked
    span_delete.onclick = closeModalDelete;
    // Close the modal when clicking outside of it
    window.onclick = function(event) {
        if (event.target == modal_delete) {
            closeModalDelete();
        }
    }
});
document.addEventListener("DOMContentLoaded", function() {
    modal_connection = document.getElementById("myModalConnection");
    span_connection = document.getElementsByClassName("close")[0];
    // Close the modal when the close button is clicked
    span_connection.onclick = closeModalConnection;
    // Close the modal when clicking outside of it
    window.onclick = function(event) {
        if (event.target == modal_connection) {
            closeModalConnection();
        }
    }
});



document.getElementById('generateSessionBtn').addEventListener('click', function () {
    const generateSessionBtn = document.getElementById('generateSessionBtn');

    // Check if the element is disabled
    if (generateSessionBtn.disabled) {
        return; // Exit the function if the element is disabled
    }
    openModalCreate();
    const xhr = new XMLHttpRequest();
    document.getElementById('result').innerHTML = `
          <p>Generating session... Do not click the above button again. This might take a few minutes.</p>
      `;
    document.getElementById("generateSessionBtn").disabled = true;
    xhr.open('POST', '/create_container', true);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  
    xhr.onload = function () {
      closeModalCreate();
      if (xhr.status >= 200 && xhr.status < 300) {
        const response = JSON.parse(xhr.responseText);
        document.getElementById("generateSessionBtn").disabled = false;
        displayResult(response);
        refreshContainers();
      } else {
        const response = JSON.parse(xhr.responseText);
        // Find out the error code and display the corresponding error message
        if (response.code === 1002) { // MAX_ERROR
          alert('You have reached the maximum number of containers. Please delete one to create another.');
        } else if (response.code === 2) { // UNKNOWN_ERROR
          document.getElementById('result').innerHTML = '<p>Error generating session. Please try again.</p>';
        } else { // UNKNOWN_ERROR
          document.getElementById('result').innerHTML = '<p>Error generating session. Please try again.</p>';
        }
        console.error('Error:', xhr.responseText);
        document.getElementById('result').innerHTML = '<p>Error generating session. Please try again.</p>';
      }
    };
  
    xhr.onerror = function () {
      closeModalCreate();
      console.error('Request failed');
      document.getElementById('result').innerHTML = '<p>Request failed. Please check your connection.</p>';
    };
  
    xhr.send(JSON.stringify({})); // Send an empty object or any required params
  });
  
  function displayResult(data) {
    document.getElementById('result').innerHTML = `
          <h3>Session Details:</h3><br>
          <p><strong>Name:</strong> ${data.name}</p><br>
          <p><strong>Username:</strong> ${data.username}</p><br>
          <p><strong>Password:</strong> ${data.password}</p><br>
          <p><strong>Hostname:</strong> ${data.hostname}</p><br>
          <p><strong>Port:</strong> ${data.port}</p><br>
          <p><strong>SSH Command:</strong> <code>${data.ssh_command}</code></p><br>
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
      <button id="restart-btn-${container.name}" class="restart-btn">Restart</button>
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
      const restartBtns = document.getElementsByClassName('restart-btn');
      for (let i = 0; i < restartBtns.length; i++) {
        restartBtns[i].addEventListener('click', function () {
          const containerId = this.id.split('-')[2];
          restartContainer(containerId);
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
      <button id="restart-btn-${container.name}" class="restart-btn">Restart</button>
      <button class="connect-btn" id="connect-btn-${container.name}">Connect</button>
    </div>
  </li>`;
            const containernametodelete = container.name;
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
          for (let i = 0; i < restartBtns.length; i++) {
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
          for (let i = 0; i < restartBtns.length; i++) {
            restartBtns[i].addEventListener('click', function () {
              const containerId = this.id.split('-')[2];
              restartContainer(containerId);
            });
          }
        } else {
          containersDiv.innerHTML = '<center><p>No containers assigned.</p></center>';
        }
      })
      .catch(error => {
        console.error('Error fetching containers:', error);
        document.getElementById('containers').innerHTML = '<p>Error fetching containers. Please try again.</p>';
      });
  };
  
  function deleteContainer(containerId) {
    if (confirm('Are you sure you want to delete this container?')) {
      openModalDelete();
      fetch(`/delete_container?id=${containerId}`, { method: 'DELETE' })
        .then(response => {
          closeModalDelete();
          if (response.ok) {
            refreshContainers();
          } else {
            console.error('Error deleting container:', response.statusText);
            alert('Error deleting container. Please try again.');
          }
        })
        .catch(error => {
          closeModalDelete();
          console.error('Error deleting container:', error);
          alert('Error deleting container. Please try again.');
        });
    }
  }

  function restartContainer(containerId) {
    if (confirm('Are you sure you want to restart this container?')) {
      openModal();
      fetch(`/container/restart?id=${containerId}`, { method: 'POST' })
        .then(response => {
          closeModal();
          if (response.ok) {
            refreshContainers();
          } else {
            console.error('Error restarting container:', response.statusText);
            alert('Error restarting container. Please try again.');
          }
        })
        .catch(error => {
          closeModal();
          console.error('Error restarting container:', error);
          alert('Error restarting container. Please try again. Check console logs for more details.');
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
                <div class="tooltip-wrapper">
                    <strong>Development Port:</strong> 80->${data.exposed_port}
                    <div class="tooltip-container">
                        <span class="question-mark">?</span>
                        <div class="tooltip-content">Development Port is to expose the port 80 inside the container to port ${data.exposed_port} accessible outside using the current URL.</div>
                    </div>
                </div>
                <strong>Active?</strong> ${data.active ? 'Yes' : 'No'}<br>
                <strong>SSH Command:</strong> <code>${data.ssh_command}</code>
            `;
            // Show the popup
            openModalConnection()


            // Tooltip functionality
            const tooltipContainers = document.querySelectorAll('.tooltip-container');
            const tooltipContents = document.querySelectorAll('.tooltip-content');

            tooltipContainers.forEach((container, index) => {
                container.addEventListener('mouseenter', () => {
                    tooltipContents[index].style.display = 'block';
                });

                container.addEventListener('mouseleave', () => {
                    tooltipContents[index].style.display = 'none';
                });
            });
        })
        .catch(error => {
            console.error('Error fetching connection details:', error);
            document.getElementById('connectionDetails').innerHTML = '<p>Error fetching connection details. Please check your internet connection.</p>';
            openModalConnection()
        });
}

// Event listener for dynamically created connect buttons
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('connect-btn')) {
        const containerId = event.target.id.split('-')[2]; // Get container ID from button ID
        openConnectionPopup(containerId); // Open new connection details popup
    }
});