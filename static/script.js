// Get dropzone and button
const dropZone = document.getElementById('drop-zone');
const newSessionButton = document.getElementById('new-session');

// Add event listeners for the dropzone
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault(); // Allow dropping
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('dragover');

  const files = e.dataTransfer.files;

  if (files.length > 0) {
    const file = files[0];

    // Check if the file is a JSON file by its type or extension
    if (file.type === 'application/json' || file.name.endsWith('.json')) {
      const reader = new FileReader();

      // Set up the event for when the file is read
      reader.onload = (event) => {
        try {
          const fileContent = event.target.result; // Get content as text
          const jsonContent = JSON.parse(fileContent); // Parse the content as JSON

          // Send the data to Flask using a POST request
          fetch('/save-json', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(jsonContent), // Send the JSON data to Flask
          })
          .then(response => response.json())  // Handling the response from Flask
          .then(data => {
            console.log('Data sent to Flask:', data); // Log response from Flask
            window.location.href = '/home?session_flag=restore'
          })
          .catch(error => {
            console.error('Error al enviar datos:', error);
            alert('Hubo un error al enviar los datos.');
          });

        } catch (err) {
          console.error('Error al parsear JSON:', err);
          alert('El archivo contiene JSON no válido.');
        }
      };

      // Handle errors during file reading
      reader.onerror = () => {
        alert('Hubo un error al leer el archivo.');
      };

      // Read the file as text
      reader.readAsText(file);
    } else {
      alert(`Tipo de archivo no válido: "${file.name}". Por favor, sube un archivo JSON.`);
    }
  } else {
    alert('No se detectó un archivo. Por favor, sube un archivo JSON válido.');
  }
});

// New session button functionality
newSessionButton.addEventListener('click', () => {
  // Redirige a la página 'home' sin pasar los datos en la URL
  window.location.href = '/home'; // Los datos seguirán estando en localStorage
});
