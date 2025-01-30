document.getElementById('generate_key').addEventListener('click', function () {
    const xhr = new XMLHttpRequest();
    document.getElementById("generate_key").disabled = true;
    xhr.open('POST', '/apikey/generate', true);
  
    xhr.onload = function () {
      if (xhr.status >= 200 && xhr.status < 300) {
        document.getElementById('messages').innerHTML = xhr.responseText;
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

    // Redirect users to the logout page
    window.location.href = '/logout';
});