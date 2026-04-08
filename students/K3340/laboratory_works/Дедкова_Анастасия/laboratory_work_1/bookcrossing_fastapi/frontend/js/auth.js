const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const messageEl = document.getElementById("message");

if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        try {
            const data = await apiRequest("/auth/login", {
                method: "POST",
                body: JSON.stringify({ username, password })
            });

            setToken(data.access_token);
            window.location.href = "books.html";
        } catch (error) {
            messageEl.textContent = error.message;
        }
    });
}

if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const email = document.getElementById("email").value;
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        try {
            const data = await apiRequest("/auth/register", {
                method: "POST",
                body: JSON.stringify({ email, username, password })
            });

            setToken(data.access_token);
            messageEl.textContent = "Регистрация успешна";
            messageEl.classList.add("success");

            setTimeout(() => {
                window.location.href = "books.html";
            }, 700);
        } catch (error) {
            messageEl.textContent = error.message;
        }
    });
}