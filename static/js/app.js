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
    const favBtn = document.getElementById("favBtn");
    const favConfirm = document.getElementById("favConfirm");
    const publishBtn = document.getElementById("publishBtn");
    const publishError = document.getElementById("publishError");
    const publishSuccess = document.getElementById("publishSuccess");
    const scheduleCheck = document.getElementById("scheduleCheck");
    const publishDate = document.getElementById("publishDate");
    const favoritesList = document.getElementById("favoritesList");
    const clearFavBtn = document.getElementById("clearFavBtn");

    let currentPost = null;

    // Генерация поста
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorBlock.classList.add("hidden");
        resultBlock.classList.add("hidden");
        publishError.classList.add("hidden");
        publishSuccess.classList.add("hidden");
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
                currentPost = data;
                // Отображаем текст с поддержкой Markdown (жирный шрифт)
                postText.innerHTML = data.text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
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

    // Копирование
    copyBtn.addEventListener("click", () => {
        if (!currentPost) return;
        const fullText = currentPost.text + "\n\n" + currentPost.hashtags.join(" ");
        navigator.clipboard.writeText(fullText).then(() => {
            copyConfirm.classList.remove("hidden");
            setTimeout(() => copyConfirm.classList.add("hidden"), 2000);
        });
    });

    // В избранное
    favBtn.addEventListener("click", async () => {
        if (!currentPost) return;
        try {
            const response = await fetch("/favorites", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(currentPost)
            });
            const data = await response.json();
            if (data.status === "ok") {
                favConfirm.classList.remove("hidden");
                setTimeout(() => favConfirm.classList.add("hidden"), 2000);
                loadFavorites();
            }
        } catch (err) {
            alert("Ошибка при сохранении");
        }
    });

    // Публикация в ВК
    publishBtn.addEventListener("click", async () => {
        if (!currentPost) return;
        publishError.classList.add("hidden");
        publishSuccess.classList.add("hidden");

        const payload = {
            text: currentPost.text,
            hashtags: currentPost.hashtags
        };

        if (scheduleCheck.checked && publishDate.value) {
            payload.publish_date = publishDate.value;
        }

        try {
            const response = await fetch("/publish-vk", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            if (data.status === "ok") {
                publishSuccess.textContent = scheduleCheck.checked 
                    ? "Запланировано!" 
                    : "Опубликовано!";
                publishSuccess.classList.remove("hidden");
            } else {
                publishError.textContent = data.message;
                publishError.classList.remove("hidden");
            }
        } catch (err) {
            publishError.textContent = "Ошибка публикации";
            publishError.classList.remove("hidden");
        }
    });

    // Показать/скрыть выбор даты
    scheduleCheck.addEventListener("change", () => {
        publishDate.classList.toggle("hidden", !scheduleCheck.checked);
    });

    // Загрузка избранного
    async function loadFavorites() {
        try {
            const response = await fetch("/favorites");
            const favorites = await response.json();
            favoritesList.innerHTML = "";
            favorites.forEach(fav => {
                const div = document.createElement("div");
                div.className = "fav-item";
                div.innerHTML = `
                    <div class="fav-item-text">${fav.text}</div>
                    <div class="fav-item-meta">Сохранено: ${fav.saved_at || "—"}</div>
                    <div class="fav-item-actions">
                        <button class="btn-copy-fav" onclick="copyFavText(this)">Копировать</button>
                        <button class="btn-delete" onclick="deleteFav(${fav.id})">Удалить</button>
                    </div>
                `;
                div.querySelector(".btn-copy-fav").addEventListener("click", () => {
                    const fullText = fav.text + "\n\n" + fav.hashtags.join(" ");
                    navigator.clipboard.writeText(fullText);
                    alert("Скопировано!");
                });
                div.querySelector(".btn-delete").addEventListener("click", async () => {
                    await fetch(`/favorites?id=${fav.id}`, { method: "DELETE" });
                    loadFavorites();
                });
                favoritesList.appendChild(div);
            });
        } catch (err) {
            favoritesList.innerHTML = "<p>Нет сохраненных постов</p>";
        }
    }

    // Генерация изображения
    const genImageBtn = document.getElementById("genImageBtn");
    const imageConfirm = document.getElementById("imageConfirm");
    const imageContainer = document.getElementById("imageContainer");
    const generatedImage = document.getElementById("generatedImage");

    genImageBtn.addEventListener("click", async () => {
        if (!currentPost) return;
        genImageBtn.disabled = true;
        genImageBtn.textContent = "Генерация...";
        imageConfirm.classList.add("hidden");

        try {
            const response = await fetch("/generate-image", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: currentPost.text })
            });
            const data = await response.json();
            if (data.status === "ok") {
                // Force reload image by adding timestamp
                generatedImage.src = data.image_url + "?t=" + new Date().getTime();
                imageContainer.classList.remove("hidden");
                imageConfirm.classList.remove("hidden");
            } else {
                alert("Ошибка: " + data.message);
            }
        } catch (err) {
            alert("Ошибка генерации изображения");
        } finally {
            genImageBtn.disabled = false;
            genImageBtn.textContent = "Создать изображение";
        }
    });
    clearFavBtn.addEventListener("click", async () => {
        if (confirm("Очистить все избранное?")) {
            await fetch("/favorites", { method: "DELETE" });
            loadFavorites();
        }
    });

    // Загружаем избранное при старте
    loadFavorites();
});
