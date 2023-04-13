// Get the file input element
const fileInput = document.getElementById('file-input');

// Add event listener for file input change
fileInput.addEventListener('change', () => {
  // Get the selected file
  const selectedFile = fileInput.files[0];
  // Create a new FormData object
  const formData = new FormData();
  // Add the selected file to the form data object
  formData.append('file', selectedFile);
  // Send a POST request to the /upload route with the form data
  fetch('/upload', {
    method: 'POST',
    body: formData
  })
  .then(() => {
    // Reload the page to show the new file
    location.reload();
  });
});

