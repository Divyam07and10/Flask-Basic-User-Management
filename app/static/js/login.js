document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = {
        email: document.getElementById("email").value,
        password: document.getElementById("password").value
    };

    const res = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        credentials: "include" // <--- important to receive cookies
    });

    const result = await res.json();

    if (res.status === 200) {
        window.location.href = "/auth/dashboard";
    } else {
        document.getElementById("loginMessage").innerText = result.message;
    }
});
