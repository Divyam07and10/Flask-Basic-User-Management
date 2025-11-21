document.getElementById("createUserForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const token = localStorage.getItem("access_token");

    const data = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        password: document.getElementById("password").value
    };

    const res = await fetch("/users/create", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify(data)
    });

    const result = await res.json();
    document.getElementById("createMessage").innerText = result.message;
});
