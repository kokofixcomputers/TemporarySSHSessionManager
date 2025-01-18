function confirmModal(message) {
    return new Promise((resolve) => {
        // Get elements
        const confirmModal = document.getElementById('confirmModal');
        const closeIcon = document.querySelector('.connclose');
        const okBtn = document.getElementById('okBtn');
        const cancelBtn = document.getElementById('cancelBtn');
        const connmodalcontent = document.getElementById('connmodal-content');

        // Set the message in the modal
        connmodalcontent.querySelector('p').textContent = message;

        // Show the modal
        confirmModal.style.display = 'block';

        // Close the modal when clicking "Cancel"
        cancelBtn.onclick = function () {
            confirmModal.style.display = 'none';
            resolve(false); // User clicked Cancel
        };

        // Handle "OK" button click
        okBtn.onclick = function () {
            confirmModal.style.display = 'none';
            resolve(true); // User clicked OK
        };

        // Close the modal if clicking outside of it
        window.onclick = function (event) {
            if (event.target === confirmModal) {
                confirmModal.style.display = 'none';
                resolve(false); // User clicked outside, treat as Cancel
            }
        };

        // Close icon functionality
        closeIcon.onclick = function () {
            confirmModal.style.display = 'none';
            resolve(false); // User closed the modal, treat as Cancel
        };
    });
}