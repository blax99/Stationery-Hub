// navbar.js
const searchButton = document.getElementById("searchButton");
const searchBox = document.getElementById("searchBox");
const searchInput = document.getElementById("searchInput");
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