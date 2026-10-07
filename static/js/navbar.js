// navbar.js
(() => {
const searchButton = document.getElementById("searchButton");
const searchBox = document.getElementById("searchBox");
const searchInput = document.getElementById("searchInput");
const menuButton = document.getElementById("menuButton");
const mobileMenu = document.getElementById("mobileMenu");
const menuIcon = document.getElementById("menuIcon");
const authLink = document.getElementById("authLink");
const userMenu = document.getElementById("userMenu");
const logoutButton = document.getElementById("logoutButton");

searchButton?.addEventListener("click", () => {
    searchBox.classList.remove("hidden");
    searchButton.classList.add("hidden");
    searchInput.focus()
});

document.addEventListener("click", (event) => {
    // If clicked outside the search area
    if (searchBox && searchButton && !searchBox.contains(event.target) && !searchButton.contains(event.target)) {
        searchBox.classList.add("hidden");
        searchButton.classList.remove("hidden");
    }
});


menuButton?.addEventListener("click", () => {
    mobileMenu.classList.toggle("hidden");

    if (mobileMenu.classList.contains("hidden")) {
        menuIcon.classList.remove("fa-xmark");
        menuIcon.classList.add("fa-bars");
    } else {
        menuIcon.classList.remove("fa-bars");
        menuIcon.classList.add("fa-xmark");
    }
});

logoutButton?.addEventListener("click", () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = authLink.dataset.loginPage;
});

async function showAuthenticatedUser() {
    const token = localStorage.getItem("access_token");
    if (!token || !authLink) return;

    try {
        const response = await fetch(authLink.dataset.profileUrl, {
            headers: { Authorization: "Bearer " + token },
        });

        if (response.status === 401) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            return;
        }
        if (!response.ok) {
            throw new Error(`Could not load profile: ${response.status}`);
        }

        const user = await response.json();
        const initials = user.username
            .split(/\s+/)
            .map((part) => part[0])
            .join("")
            .slice(0, 2)
            .toUpperCase();
        const circle = document.createElement("span");
        circle.className =
            "flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-xs font-semibold text-white";
        circle.textContent = initials;
        circle.setAttribute("aria-hidden", "true");

        const name = document.createElement("span");
        name.className = "max-w-32 truncate";
        name.textContent = user.username;

        authLink.replaceChildren(circle, name);
        authLink.href = authLink.dataset.profilePage;
        authLink.className =
            "flex items-center gap-2 text-gray-800 hover:text-blue-600 transition text-sm font-medium";
        authLink.setAttribute("aria-label", `View profile for ${user.username}`);
        userMenu.classList.add("group");
    } catch (error) {
        console.error("Unable to display the signed-in user.", error);
    }
}

showAuthenticatedUser();
})();
