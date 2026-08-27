// navbar.js
(() => {
const searchButton = document.getElementById("searchButton");
const searchBox = document.getElementById("searchBox");
const searchInput = document.getElementById("searchInput");
const menuButton = document.getElementById("menuButton");
const mobileMenu = document.getElementById("mobileMenu");
const menuIcon = document.getElementById("menuIcon");
console.log('navbar');


searchButton.addEventListener("click", () => {
    searchBox.classList.remove("hidden");
    searchButton.classList.add("hidden");
    searchInput.focus()
});

document.addEventListener("click", (event) => {
    // If clicked outside the search area
    if (!searchBox.contains(event.target) && !searchButton.contains(event.target)) {
        searchBox.classList.add("hidden");
        searchButton.classList.remove("hidden");
    }
});


menuButton.addEventListener("click", () => {
    mobileMenu.classList.toggle("hidden");

    if (mobileMenu.classList.contains("hidden")) {
        menuIcon.classList.remove("fa-xmark");
        menuIcon.classList.add("fa-bars");
    } else {
        menuIcon.classList.remove("fa-bars");
        menuIcon.classList.add("fa-xmark");
    }
});
})();
