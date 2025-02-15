document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const resultHeading = document.querySelector("h2");

    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault(); // Empêcher le rechargement de la page

            const formData = new FormData(form);

            fetch("/predict", {
                method: "POST",
                body: formData,
            })
                .then((response) => response.json())
                .then((data) => {
                    if (resultHeading) {
                        resultHeading.textContent = `Sentiment: ${data.prediction_text}`;
                        resultHeading.style.display = "block";
                    }
                })
                .catch((error) => {
                    console.error("Erreur :", error);
                });
        });
    }
});