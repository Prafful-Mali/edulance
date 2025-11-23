function getAccessToken() {
    return localStorage.getItem("access_token");
}

function getRefreshToken() {
    return localStorage.getItem("refresh_token");
}

function isAuthenticated() {
    return !!getAccessToken();
}

function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = "/login/";
        return false;
    }
    return true;
}

async function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
        return false;
    }

    try {
        const response = await fetch("/api/token/", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ refresh: refreshToken })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("access_token", data.access);
            localStorage.setItem("refresh_token", data.refresh);
            return true;
        }
    } catch (error) {
        console.error("Error refreshing token:", error);
    }

    return false;
}

async function authenticatedFetch(url, options) {
    const token = getAccessToken();
    if (!token) {
        throw new Error("No access token available");
    }

    if (!options) {
        options = {};
    }

    if (!options.headers) {
        options.headers = {};
    }

    options.headers["Authorization"] = "Bearer " + token;

    let response = await fetch(url, options);

    if (response.status === 401) {
        const refreshed = await refreshAccessToken();

        if (refreshed) {
            const newToken = getAccessToken();
            options.headers["Authorization"] = "Bearer " + newToken;
            response = await fetch(url, options);
        } else {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            localStorage.removeItem("user_id");

            window.location.href = "/login/";
        }
    }

    return response;
}

document.getElementById("logoutBtn").addEventListener("click", async function (e) {
    e.preventDefault();

    if (confirm("Are you sure you want to logout?")) {
        try {
            const refreshToken = getRefreshToken();
            await authenticatedFetch("/api/logout/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ refresh: refreshToken })
            });
        } catch (error) {
            console.error("Error during logout:", error);
        }

        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user_id");

        window.location.href = "/login/";
    }
});