protectPage();

async function getCurrentUser() {
    return await apiRequest("/users/me");
}

async function requestExchange(bookId) {
    try {
        const message = prompt("Введите сообщение владельцу книги:", "Хочу обменяться этой книгой");
        if (message === null) return;

        await apiRequest(`/books/${bookId}/request`, {
            method: "POST",
            body: JSON.stringify({
                message: message
            })
        });

        alert("Запрос на обмен отправлен");
    } catch (error) {
        alert(error.message);
    }
}

async function loadAllBooks() {
    const container = document.getElementById("booksList");
    if (!container) return;

    try {
        const books = await apiRequest("/books/available");
        const currentUser = await getCurrentUser();

        container.innerHTML = "";

        books.forEach(book => {
            const card = document.createElement("div");
            card.className = "book-card";

            const canRequest = book.owner_id !== currentUser.id && book.status === "available";

            card.innerHTML = `
                <h3>${book.title}</h3>
                <p class="book-meta">Автор: ${book.author}</p>
                <p>${book.description || "Без описания"}</p>
                <p class="book-meta">Состояние: ${book.condition}</p>
                <span class="status">${book.status}</span>
                ${
                    canRequest
                        ? `<div style="margin-top: 14px;">
                               <button class="primary request-btn" data-book-id="${book.id}">
                                   Взять книгу
                               </button>
                           </div>`
                        : ""
                }
            `;
            container.appendChild(card);
        });

        document.querySelectorAll(".request-btn").forEach(button => {
            button.addEventListener("click", () => {
                const bookId = Number(button.dataset.bookId);
                requestExchange(bookId);
            });
        });
    } catch (error) {
        container.innerHTML = `<p>${error.message}</p>`;
    }
}

async function loadMyBooks() {
    const container = document.getElementById("myBooksList");
    if (!container) return;

    try {
        const data = await apiRequest("/users/me/books");
        container.innerHTML = "";

        data.books.forEach(book => {
            const card = document.createElement("div");
            card.className = "book-card";
            card.innerHTML = `
                <h3>${book.title}</h3>
                <p class="book-meta">Автор: ${book.author}</p>
                <p>${book.description || "Без описания"}</p>
                <p class="book-meta">Состояние: ${book.condition}</p>
                <span class="status">${book.status}</span>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        container.innerHTML = `<p>${error.message}</p>`;
    }
}

const addBookForm = document.getElementById("addBookForm");
if (addBookForm) {
    addBookForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const message = document.getElementById("message");

        try {
            const currentUser = await getCurrentUser();

            await apiRequest("/books/", {
                method: "POST",
                body: JSON.stringify({
                    owner_id: currentUser.id,
                    title: document.getElementById("title").value,
                    author: document.getElementById("author").value,
                    description: document.getElementById("description").value,
                    condition: document.getElementById("condition").value,
                    status: "available"
                })
            });

            message.textContent = "Книга добавлена";
            message.classList.add("success");
            addBookForm.reset();
        } catch (error) {
            message.textContent = error.message;
        }
    });
}

loadAllBooks();
loadMyBooks();