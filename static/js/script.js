document.addEventListener('DOMContentLoaded', () => {
    const youtubeUrlInput = document.getElementById('youtube-url');
    const processBtnInput = document.getElementById('process-btn');
    const resultDiv = document.getElementById('result');
    const linkedinPostTextarea = document.getElementById('linkedin-post');
    const copyBtn = document.getElementById('copy-btn');
    const loadingDiv = document.getElementById('loading');

    particlesJS.load('particles-js', '/static/particles.json', function() {
        console.log('callback - particles.js config loaded');
    });

    processBtnInput.addEventListener('click', async () => {
        const youtubeUrl = youtubeUrlInput.value.trim();
        if (!youtubeUrl) {
            alert('Syötä kelvollinen YouTube-URL');
            return;
        }

        resultDiv.classList.add('hidden');
        loadingDiv.classList.remove('hidden');

        try {
            const response = await fetch('/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: youtubeUrl }),
            });

            const data = await response.json();

            if (response.ok) {
                linkedinPostTextarea.value = data.linkedin_post;
                resultDiv.classList.remove('hidden');
            } else {
                alert(`Virhe: ${data.error}`);
            }
        } catch (error) {
            alert('Tapahtui virhe käsiteltäessä pyyntöä');
        } finally {
            loadingDiv.classList.add('hidden');
        }
    });

    copyBtn.addEventListener('click', () => {
        linkedinPostTextarea.select();
        document.execCommand('copy');
        // Muutetaan kopiointi-ilmoitus
        copyBtn.textContent = 'Kopioitu';
        setTimeout(() => {
            copyBtn.textContent = 'Kopioi';
        }, 2000); // Palautetaan alkuperäinen teksti 2 sekunnin kuluttua
    });
});