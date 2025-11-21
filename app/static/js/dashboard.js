document.addEventListener("DOMContentLoaded", async () => {
    try {
        const res = await fetch("/auth/dashboard/data");
        if (res.ok) {
            const data = await res.json();
            document.getElementById("dashboardData").innerText =
                `Last Login: ${data.last_login ? new Date(data.last_login).toLocaleString() : 'Never'}`;
        } else {
            document.getElementById("dashboardData").innerText =
                "Error loading data";
        }
    } catch (e) {
        document.getElementById("dashboardData").innerText =
            "Error loading data";
    }
});
