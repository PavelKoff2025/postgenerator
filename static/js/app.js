document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("urlForm");
    const urlInput = document.getElementById("urlInput");
    const generateBtn = document.getElementById("generateBtn");
    const btnText = document.getElementById("btnText");
    const btnLoader = document.getElementById("btnLoader");
    const errorBlock = document.getElementById("errorBlock");
    const resultBlock = document.getElementById("resultBlock");
    const postText = document.getElementById("postText");
    const hashtags = document.getElementById("hashtags");
    const copyBtn = document.getElementById("copyBtn");
    const copyConfirm = document.getElementById("copyConfirm");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorBlock.classList.add("hidden");
        resultBlock.classList.add("hidden");
        generateBtn.disabled = true;
        btnText.classList.add("hidden");
        btnLoader.classList.remove("hidden");

        try {
            const response = await fetch("/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: urlInput.value })
            });

            const data = await response.json();

            if (data.status === "ok") {
                postText.textContent = data.text;
                hashtags.innerHTML = data.hashtags
                    .map(tag => `<span class="hashtag">${tag}</span>`)
                    .join("");
                resultBlock.classList.remove("hidden");
            } else {
                errorBlock.textContent = data.message || "Произошла ошибка";
                errorBlock.classList.remove("hidden");
            }
        } catch (err) {
            errorBlock.textContent = "Ошибка соединения с сервером";
            errorBlock.classList.remove("hidden");
        } finally {
            generateBtn.disabled = false;
            btnText.classList.remove("hidden");
            btnLoader.classList.add("hidden");
        }
    });

    copyBtn.addEventListener("click", () => {
        const fullText = postText.textContent + "\n\n" + hashtags.textContent;
        navigator.clipboard.writeText(fullText).then(() => {
            copyConfirm.classList.remove("hidden");
            setTimeout(() => copyConfirm.classList.add("hidden"), 2000);
        });
    });
});
