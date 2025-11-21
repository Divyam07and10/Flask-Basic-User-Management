async function deleteUser(id) {
    if (!confirm("Deactivate this account?")) return;

    const res = await fetch(`/users/${id}`, {
        method: "DELETE",
        credentials: "include",
    });

    const result = await res.json();
    alert(result.message || "Account updated");
    location.reload();
}
