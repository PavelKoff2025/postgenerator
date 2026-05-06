document.addEventListener("DOMContentLoaded", function() {
    // Get elements
    var form = document.getElementById("urlForm");
    var urlInput = document.getElementById("urlInput");
    var generateBtn = document.getElementById("generateBtn");
    var btnText = document.getElementById("btnText");
    var btnLoader = document.getElementById("btnLoader");
    var errorBlock = document.getElementById("errorBlock");
    var resultBlock = document.getElementById("resultBlock");
    var postText = document.getElementById("postText");
    var hashtags = document.getElementById("hashtags");
    var copyBtn = document.getElementById("copyBtn");
    var copyConfirm = document.getElementById("copyConfirm");
    var favBtn = document.getElementById("favBtn");
    var favConfirm = document.getElementById("favConfirm");
    var publishBtn = document.getElementById("publishBtn");
    var publishError = document.getElementById("publishError");
    var publishSuccess = document.getElementById("publishSuccess");
    var scheduleCheck = document.getElementById("scheduleCheck");
    var publishDate = document.getElementById("publishDate");
    var favoritesList = document.getElementById("favoritesList");
    var clearFavBtn = document.getElementById("clearFavBtn");
    var genImageBtn = document.getElementById("genImageBtn");
    var imageConfirm = document.getElementById("imageConfirm");
    var imageContainer = document.getElementById("imageContainer");
    var generatedImage = document.getElementById("generatedImage");

    var currentPost = null;

    // Generate post
    form.addEventListener("submit", async function(e) {
        e.preventDefault();
        errorBlock.classList.add("hidden");
        resultBlock.classList.add("hidden");
        publishError.classList.add("hidden");
        publishSuccess.classList.add("hidden");
        generateBtn.disabled = true;
        btnText.classList.add("hidden");
        btnLoader.classList.remove("hidden");

        try {
            var response = await fetch("/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: urlInput.value })
            });
            var data = await response.json();

            if (data.status === "ok") {
                currentPost = data;
                postText.innerHTML = data.text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                hashtags.innerHTML = data.hashtags
                    .map(function(tag) { return '<span class="hashtag">' + tag + '</span>'; })
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

    // Copy
    copyBtn.addEventListener("click", function() {
        if (!currentPost) return;
        var fullText = currentPost.text + "\n\n" + currentPost.hashtags.join(" ");
        navigator.clipboard.writeText(fullText).then(function() {
            copyConfirm.classList.remove("hidden");
            setTimeout(function() { copyConfirm.classList.add("hidden"); }, 2000);
        });
    });

    // Favorites
    favBtn.addEventListener("click", async function() {
        if (!currentPost) return;
        try {
            var response = await fetch("/favorites", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(currentPost)
            });
            var data = await response.json();
            if (data.status === "ok") {
                favConfirm.classList.remove("hidden");
                setTimeout(function() { favConfirm.classList.add("hidden"); }, 2000);
                loadFavorites();
            }
        } catch (err) {
            alert("Ошибка при сохранении");
        }
    });

    // Publish to VK
    publishBtn.addEventListener("click", async function() {
        if (!currentPost) return;
        publishError.classList.add("hidden");
        publishSuccess.classList.add("hidden");

        var payload = {
            text: currentPost.text,
            hashtags: currentPost.hashtags
        };

        if (scheduleCheck.checked && publishDate.value) {
            payload.publish_date = publishDate.value;
        }

        try {
            var response = await fetch("/publish-vk", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            var data = await response.json();
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

    // Toggle date picker
    scheduleCheck.addEventListener("change", function() {
        publishDate.classList.toggle("hidden", !scheduleCheck.checked);
    });

    // Generate image
    genImageBtn.addEventListener("click", async function() {
        if (!currentPost) {
            alert("Сначала сгенерируйте пост!");
            return;
        }
        genImageBtn.disabled = true;
        genImageBtn.textContent = "Генерация...";
        imageConfirm.classList.add("hidden");

        try {
            console.log("Generating image for text:", currentPost.text.substring(0, 50) + "...");
            var response = await fetch("/generate-image", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: currentPost.text })
            });
            var data = await response.json();
            console.log("Image generation response:", data);
            
            if (data.status === "ok") {
                generatedImage.src = data.image_url + "?t=" + new Date().getTime();
                imageContainer.classList.remove("hidden");
                imageConfirm.classList.remove("hidden");
            } else {
                alert("Ошибка: " + (data.message || "неизвестная ошибка"));
            }
        } catch (err) {
            console.error("Image generation error:", err);
            alert("Ошибка генерации изображения");
        } finally {
            genImageBtn.disabled = false;
            genImageBtn.textContent = "Создать изображение";
        }
    });

    // Clear favorites
    clearFavBtn.addEventListener("click", async function() {
        if (confirm("Очистить все избранное?")) {
            await fetch("/favorites", { method: "DELETE" });
            loadFavorites();
        }
    });

    // Load favorites
    async function loadFavorites() {
        try {
            var response = await fetch("/favorites");
            var favorites = await response.json();
            favoritesList.innerHTML = "";
            favorites.forEach(function(fav) {
                var div = document.createElement("div");
                div.className = "fav-item";
                div.innerHTML = `
                    <div class="fav-item-text">${fav.text}</div>
                    <div class="fav-item-meta">Сохранено: ${fav.saved_at || "—"}</div>
                    <div class="fav-item-actions">
                        <button class="btn-copy-fav">Копировать</button>
                        <button class="btn-delete">Удалить</button>
                    </div>
                `;
                div.querySelector(".btn-copy-fav").addEventListener("click", function() {
                    var fullText = fav.text + "\n\n" + fav.hashtags.join(" ");
                    navigator.clipboard.writeText(fullText);
                    alert("Скопировано!");
                });
                div.querySelector(".btn-delete").addEventListener("click", async function() {
                    await fetch("/favorites?id=" + fav.id, { method: "DELETE" });
                    loadFavorites();
                });
                favoritesList.appendChild(div);
            });
        } catch (err) {
            favoritesList.innerHTML = "<p>Нет сохраненных постов</p>";
        }
    }

    // Load on start
    loadFavorites();
});
