protectPage();

async function acceptRequest(requestId) {
    try {
        await apiRequest(`/exchange-requests/${requestId}/accept`, {
            method: "POST"
        });

        await apiRequest(`/exchanges/from-request/${requestId}`, {
            method: "POST"
        });

        alert("Запрос принят, обмен создан");
        loadRequests();
    } catch (error) {
        alert(error.message);
    }
}

async function rejectRequest(requestId) {
    try {
        await apiRequest(`/exchange-requests/${requestId}/reject`, {
            method: "POST"
        });

        alert("Запрос отклонён");
        loadRequests();
    } catch (error) {
        alert(error.message);
    }
}

async function loadRequests() {
    const incomingContainer = document.getElementById("incomingRequests");
    const outgoingContainer = document.getElementById("outgoingRequests");

    if (!incomingContainer || !outgoingContainer) return;

    try {
        const incoming = await apiRequest("/users/me/exchange-requests/incoming");
        const outgoing = await apiRequest("/users/me/exchange-requests/outgoing");

        incomingContainer.innerHTML = "";
        outgoingContainer.innerHTML = "";

        if (!incoming.length) {
            incomingContainer.innerHTML = "<p>Входящих запросов пока нет.</p>";
        }

        if (!outgoing.length) {
            outgoingContainer.innerHTML = "<p>Исходящих запросов пока нет.</p>";
        }

        incoming.forEach(req => {
            const card = document.createElement("div");
            card.className = "request-card";

            const canManage = req.status === "pending";

            card.innerHTML = `
                <h3>Запрос #${req.id}</h3>
                <p class="request-meta">Книга: ${req.book?.title || "Неизвестно"}</p>
                <p class="request-meta">Автор: ${req.book?.author || "Неизвестно"}</p>
                <p class="request-meta">От пользователя: ${req.requester?.username || "Неизвестно"}</p>
                <p>${req.message || "Без сообщения"}</p>
                <span class="status">${req.status}</span>
                ${
                    canManage
                        ? `<div style="margin-top: 14px; display: flex; gap: 10px; flex-wrap: wrap;">
                               <button class="primary accept-btn" data-id="${req.id}">Принять</button>
                               <button class="primary reject-btn" data-id="${req.id}" style="background:#dc2626;">Отклонить</button>
                           </div>`
                        : ""
                }
            `;
            incomingContainer.appendChild(card);
        });

        outgoing.forEach(req => {
            const card = document.createElement("div");
            card.className = "request-card";
            card.innerHTML = `
                <h3>Запрос #${req.id}</h3>
                <p class="request-meta">Книга: ${req.book?.title || "Неизвестно"}</p>
                <p class="request-meta">Автор: ${req.book?.author || "Неизвестно"}</p>
                <p class="request-meta">Владелец: ${req.owner?.username || "Неизвестно"}</p>
                <p>${req.message || "Без сообщения"}</p>
                <span class="status">${req.status}</span>
            `;
            outgoingContainer.appendChild(card);
        });

        document.querySelectorAll(".accept-btn").forEach(button => {
            button.addEventListener("click", () => {
                acceptRequest(Number(button.dataset.id));
            });
        });

        document.querySelectorAll(".reject-btn").forEach(button => {
            button.addEventListener("click", () => {
                rejectRequest(Number(button.dataset.id));
            });
        });
    } catch (error) {
        incomingContainer.innerHTML = `<p>${error.message}</p>`;
        outgoingContainer.innerHTML = `<p>${error.message}</p>`;
    }
}

loadRequests();