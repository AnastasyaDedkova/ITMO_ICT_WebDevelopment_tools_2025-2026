const API_BASE = "http://127.0.0.1:8000";

function getToken() {
    return localStorage.getItem("access_token");
}

function setToken(token) {
    localStorage.setItem("access_token", token);
}

function removeToken() {
    localStorage.removeItem("access_token");
}

function authHeaders() {
    const token = getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
}

async function apiRequest(url, options = {}) {
    const response = await fetch(`${API_BASE}${url}`, {
        headers: {
            "Content-Type": "application/json",
            ...authHeaders(),
            ...(options.headers || {})
        },
        ...options
    });

    if (!response.ok) {
        let errorText = "Ошибка запроса";
        try {
            const errorData = await response.json();
            errorText = errorData.detail || JSON.stringify(errorData);
        } catch {
            errorText = response.statusText;
        }
        throw new Error(errorText);
    }

    if (response.status === 204) return null;
    return response.json();
}

function logout() {
    removeToken();
    window.location.href = "login.html";
}

function protectPage() {
    if (!getToken()) {
        window.location.href = "login.html";
    }
}