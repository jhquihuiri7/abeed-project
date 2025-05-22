// launcher.js

init();

function init() {
  document.addEventListener("DOMContentLoaded", () => {
    add_listeners();
  });

  function add_listeners() {
    document.querySelector("#new-session").addEventListener("click", () => {
      window.location.href = "/home?session_flag=new";
    });

    document.querySelector(".content").addEventListener("click", (event) => {
      const button = event.target;
      if (button.tagName === "BUTTON" && button.dataset.filename) {
        const fileName = button.dataset.filename;
        handlePredefined(fileName);
      }
    });

    document
      .querySelector("#session-upload")
      .addEventListener("change", handleFileUpload);
  }

  function handleFileUpload() {
    const fileInput = document.querySelector("#session-upload");
    const file = fileInput.files[0];
    const fileName = file.name.toLowerCase();
    const isJson =
      file.type === "application/json" || fileName.endsWith(".json");
    const isCsv = file.type === "text/csv" || fileName.endsWith(".csv");
    if (isJson) {
      const reader = new FileReader();
      reader.onload = (event) => {
        handleJson(event);
      };
      reader.onerror = () => {
        alert("Error reading file.");
      };
      reader.readAsText(file);
    } else if (isCsv) {
      handleCsv();
    } else {
      alert(
        `Invalid file type: "${file.name}". Please upload a JSON or CSV file.`
      );
    }

    function handleJson(event) {
      try {
        const json = JSON.parse(event.target.result);
        fetch("/save-json", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(json),
        })
          .then(() => (window.location.href = "/home?session_flag=restore"))
          .catch(() => alert("Error loading the profile."));
      } catch {
        alert("Error parsing JSON file.");
      }
    }

    function handleCsv() {
      fetch("/save-csv", {
        method: "POST",
        body: (() => {
          const formData = new FormData();
          formData.append("file", file);
          return formData;
        })(),
      })
        .then(() => (window.location.href = "/custom_dash"))
        .catch(() => alert("Error parsing CSV file."));
    }
  }
}

function handlePredefined(fileName) {
  fetch(`predefined/${fileName}`)
    .then((response) => {
      if (!response.ok) {
        return response.text().then((text) => {
          throw new Error(`${response.status} ${text}`);
        });
      }
      return response;
    })
    .then(() => {
      window.location.href = "/home?session_flag=restore";
    })
    .catch((error) => {
      alert(error);
    });
}
