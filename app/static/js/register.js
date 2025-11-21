document.getElementById("registerForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        password: document.getElementById("password").value
    };

    const res = await fetch("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const result = await res.json();
    document.getElementById("registerMessage").innerText = result.message;

    if (res.status === 201) {
        setTimeout(() => {
            window.location.href = "/auth/login";
        }, 1000);
    }
});
