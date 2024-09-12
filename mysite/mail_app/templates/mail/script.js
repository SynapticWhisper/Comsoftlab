document.addEventListener("DOMContentLoaded", function () {
    let progressBar = document.getElementById('progress-bar');
    let progressText = document.getElementById('progress-text');

    setTimeout(function () {
        progressBar.style.width = '50%';
        progressText.textContent = 'Получение сообщений...';
    }, 1000);

    setTimeout(function () {
        progressBar.style.width = '100%';
        progressText.textContent = 'Загрузка завершена';
    }, 3000);
});
