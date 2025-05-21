document.querySelector(".content").addEventListener("click", (event) => {
  const button = event.target;
  if (button.tagName === "BUTTON" && button.dataset.filename) {
    const fileName = button.dataset.filename;
    send_presaved_json(fileName);
  }
});

function send_presaved_json(fileName) {
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
