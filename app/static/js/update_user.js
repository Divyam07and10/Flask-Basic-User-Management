document.getElementById("updateUserForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const token = localStorage.getItem("access_token");
    const userId = window.location.pathname.split("/").pop();

    const data = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        dob: document.getElementById("dob").value,
        old_password: document.getElementById("old_password").value,
        new_password: document.getElementById("new_password").value
    };

    const res = await fetch(`/users/${userId}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify(data)
    });

    const result = await res.json();
    document.getElementById("updateMessage").innerText = result.message;
});
