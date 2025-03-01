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
      const reader = new FileReader(); // Crear una instancia de FileReader

  // Verifica que el lector fue creado
  console.log("FileReader creado");

  // Configurar evento para cuando el archivo sea leído
  reader.onload = (event) => {
    console.log("FileReader onload ejecutado");
    try {
      const fileContent = event.target.result; // Obtener el contenido como texto
      console.log("Contenido del archivo (string):", fileContent);
      const jsonContent = JSON.parse(fileContent); // Parsear el contenido como JSON
      console.log('Contenido JSON:', jsonContent); // Imprimir el JSON en consola
      const jsonString = encodeURIComponent(JSON.stringify(jsonContent));

          // Redirect to /home with the JSON data as a query parameter
      window.location.href = `/home?data=${jsonString}`;
        
    } catch (err) {
      console.error('Error al parsear JSON:', err);
      alert('El archivo contiene JSON no válido.');
    }
  };

  // Configurar evento para errores al leer el archivo
  reader.onerror = () => {
    console.error('Error al leer el archivo:', reader.error);
    alert('Hubo un error al leer el archivo.');
  };

  // Confirmar que se intentará leer el archivo
  console.log("Intentando leer el archivo...");

  // Leer el archivo como texto
  reader.readAsText(file);
      // Further processing logic here (e.g., reading the file content)
    } else {
      alert(`Invalid file type: "${file.name}". Please upload a JSON file.`);
    }
  } else {
    alert('No file detected. Please drop a valid JSON file.');
  }
});

// New session button functionality
newSessionButton.addEventListener('click', () => {
  window.location.href = `/home`;
});
