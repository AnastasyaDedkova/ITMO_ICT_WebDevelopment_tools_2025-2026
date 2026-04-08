protectPage();

async function completeExchange(exchangeId) {
    try {
        await apiRequest(`/exchanges/${exchangeId}/complete`, {
            method: "POST"
        });

        alert("Обмен завершён, книга убрана из доступных");
        loadExchanges();
    } catch (error) {
        alert(error.message);
    }
}

async function loadExchanges() {
    const container = document.getElementById("exchangesList");
    if (!container) return;

    try {
        const exchanges = await apiRequest("/users/me/exchanges");
        container.innerHTML = "";

        if (!exchanges.length) {
            container.innerHTML = "<p>У вас пока нет обменов.</p>";
            return;
        }

        exchanges.forEach(exchange => {
            const card = document.createElement("div");
            card.className = "exchange-card";

            const canComplete = exchange.status !== "completed";

            card.innerHTML = `
                <h3>Обмен #${exchange.id}</h3>
                <p class="exchange-meta">Запрос ID: ${exchange.request_id}</p>
                <p>Место: ${exchange.place}</p>
                <p>Дата: ${new Date(exchange.exchange_date).toLocaleString()}</p>
                <p>${exchange.comment || "Без комментария"}</p>
                <span class="status">${exchange.status}</span>
                ${
                    canComplete
                        ? `<div style="margin-top: 14px;">
                               <button class="primary complete-btn" data-id="${exchange.id}">
                                   Завершить обмен
                               </button>
                           </div>`
                        : ""
                }
            `;

            container.appendChild(card);
        });

        document.querySelectorAll(".complete-btn").forEach(button => {
            button.addEventListener("click", () => {
                completeExchange(Number(button.dataset.id));
            });
        });
    } catch (error) {
        container.innerHTML = `<p>${error.message}</p>`;
    }
}

loadExchanges();