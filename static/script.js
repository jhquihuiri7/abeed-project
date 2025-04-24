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
    const fileName = file.name.toLowerCase();
    
    if (file.type === 'application/json' || fileName.endsWith('.json')) {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const fileContent = event.target.result;
          const jsonContent = JSON.parse(fileContent);

          fetch('/save-json', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(jsonContent),
          })
          .then(response => response.json())
          .then(data => {
            console.log('Data sent to Flask:', data);
            window.location.href = '/home?session_flag=restore';
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
      reader.onerror = () => {
        alert('Hubo un error al leer el archivo.');
      };
      reader.readAsText(file);
    } else if (file.type === 'text/csv' || fileName.endsWith('.csv')) {
      const formData = new FormData();
      formData.append('file', file);

      fetch('/upload', {
        method: 'POST',
        body: formData,
      })
      .then(response => response.json())
      .then(data => {
        console.log('CSV file uploaded:', data);
        window.location.href = '/custom_dash';
      })
      .catch(error => {
        console.error('Error al cargar el archivo CSV:', error);
        alert('Hubo un error al subir el archivo CSV.');
      });
    } else {
      alert(`Tipo de archivo no válido: "${file.name}". Por favor, sube un archivo JSON o CSV.`);
    }
  } else {
    alert('No se detectó un archivo. Por favor, sube un archivo JSON o CSV válido.');
  }
});

// New session button functionality
newSessionButton.addEventListener('click', () => {
  window.location.href = '/home';
});
