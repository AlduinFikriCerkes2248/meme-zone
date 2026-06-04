const API_URL = 'http://localhost:8000';

async function fetchMemes() {
    const category = document.getElementById('categoryFilter').value;
    const sort = document.getElementById('sortOrder').value;

    let url = `${API_URL}/memes?sort=${sort}`;
    if (category) {
        url += `&category=${category}`;
    }

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Сервер відхилив запит');

        const memes = await response.json();
        renderGallery(memes);
    } catch (error) {
        console.warn('Сервер FastAPI не знайдено. Завантажую чисту базу мемів.');

        // 🔥 ЧИСТА БАЗА: Тільки ті меми, які 100% завантажилися на скріншоті 🔥
        const testMemes = [
            // --- IT 💻 ---
            { url: "https://api.memegen.link/images/fine/code_has_100_errors/this_is_fine.png", category: "IT" },
            { url: "https://api.memegen.link/images/rollsafe/cant_have_bugs/if_you_never_test_it.png", category: "IT" },
            { url: "https://api.memegen.link/images/success/task_ameba/finally_works.png", category: "IT" },

            // --- Коти 🐈 ---
            { url: "https://api.memegen.link/images/woman-cat/why_wont_it_compile/meow.png", category: "Коти" },
            { url: "https://api.memegen.link/images/doge/such_cat/very_meow.png", category: "Коти" },

            // --- Навчання 📚 ---
            { url: "https://api.memegen.link/images/db/studying_for_NMT/me/playing_rust.png", category: "Навчання" },
            { url: "https://api.memegen.link/images/spongebob/i_will_do_it_tomorrow/sure_you_will.png", category: "Навчання" },

            // --- Ігри 🎮 ---
            { url: "https://api.memegen.link/images/drake/sleeping/playing_terraria_until_4_am.png", category: "Ігри" },
            { url: "https://api.memegen.link/images/buzz/creepers/creepers_everywhere.png", category: "Ігри" },
            { url: "https://api.memegen.link/images/pigeon/is_this/a_minecraft_block.png", category: "Ігри" },

            // --- Спорт 🏋️‍♂️ ---
            { url: "https://api.memegen.link/images/drake/sleeping/going_to_the_gym.png", category: "Спорт" },
            { url: "https://api.memegen.link/images/rollsafe/muscles_wont_hurt/if_you_dont_train.png", category: "Спорт" },

            // --- Крінж 🤡 ---
            { url: "https://api.memegen.link/images/doge/such_cringe/very_wow.png", category: "Крінж" },
            { url: "https://api.memegen.link/images/spongebob/my_code_is/perfect.png", category: "Крінж" }
        ];

        const filtered = category ? testMemes.filter(m => m.category === category) : testMemes;

        if (sort === 'oldest') {
            filtered.reverse();
        }

        renderGallery(filtered);
    }
}

function renderGallery(memes) {
    const gallery = document.getElementById('memeGallery');
    gallery.innerHTML = '';

    if (memes.length === 0) {
        gallery.innerHTML = '<p style="grid-column: 1 / -1; text-align: center; color: #64748b; font-size: 1.2rem;">Мемів у цій категорії ще немає 😢</p>';
        return;
    }

    memes.forEach((meme, index) => {
        const card = document.createElement('div');
        card.className = 'meme-card';
        card.style.animationDelay = `${index * 0.05}s`;
        card.innerHTML = `
            <img src="${meme.url}" alt="Мем">
            <p>📂 ${meme.category}</p>
        `;
        gallery.appendChild(card);
    });
}

document.getElementById('addMemeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitBtn = e.target.querySelector('button');
    submitBtn.textContent = 'Завантаження... ⏳';
    submitBtn.disabled = true;

    const newMeme = {
        url: document.getElementById('memeUrl').value,
        category: document.getElementById('memeCategory').value
    };

    try {
        const response = await fetch(`${API_URL}/memes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newMeme)
        });

        if (response.ok) {
            alert('Мем успішно залетів у базу! 🔥');
            e.target.reset();
            fetchMemes();
        } else {
            alert('Помилка сервера ❌');
        }
    } catch (error) {
        alert('Бекенд недоступний. Але дизайн працює! 🚀\n(Коли сервак підніметься, мем додасться)');
    } finally {
        submitBtn.textContent = 'Запустити мем 🚀';
        submitBtn.disabled = false;
    }
});

document.getElementById('randomMemeBtn').addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_URL}/memes/random`);
        if (response.ok) {
            const randomMeme = await response.json();
            alert(`URL: ${randomMeme.url}`);
        } else {
            throw new Error('Помилка');
        }
    } catch (error) {
        const jokes = [
            "Коли нарешті доробив завдання 'Ameba', а воно не компілюється... 🦠",
            "Логіка в грі 'Перегони' на Windows Forms працює краще, ніж мій графік сну 🏎️",
            "Коли заспавнився в Rust, і одразу чуєш кроки голого тіпа з каменем... 🏃‍♂️💨",
            "Minecraft навчив мене: якщо є проблема, просто став блок. У програмуванні це називається 'try-catch' 🧱",
            "Мій код ідеальний. Помилки створюють користувачі! 💻"
        ];
        alert(jokes[Math.floor(Math.random() * jokes.length)]);
    }
});

document.getElementById('categoryFilter').addEventListener('change', fetchMemes);
document.getElementById('sortOrder').addEventListener('change', fetchMemes);

fetchMemes();