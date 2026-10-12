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
  let authStateRequest = 0;

  function showSignedOutUser() {
    authStateRequest += 1;
    authLink.replaceChildren(document.createTextNode("Sign In"));
    authLink.href = authLink.dataset.loginPage;
    authLink.className =
      "border border-black bg-white text-black px-3 sm:px-4 py-1.5 rounded-lg hover:bg-black hover:text-white transition text-sm font-medium cursor-pointer text-center";
    authLink.removeAttribute("aria-label");
    userMenu.classList.remove("group");
  }

  function getCsrfToken() {
    const cookie = document.cookie
      .split("; ")
      .find((value) => value.startsWith("csrftoken="));
    return (
      cookie?.slice("csrftoken=".length) ||
      document.querySelector(
        "#logout-csrf-form input[name=csrfmiddlewaretoken]",
      )?.value
    );
  }

  searchButton?.addEventListener("click", () => {
    searchBox.classList.remove("hidden");
    searchButton.classList.add("hidden");
    searchInput.focus();
  });

  document.addEventListener("click", (event) => {
    // If clicked outside the search area
    if (
      searchBox &&
      searchButton &&
      !searchBox.contains(event.target) &&
      !searchButton.contains(event.target)
    ) {
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

  logoutButton?.addEventListener("click", async () => {
    try {
      const response = await fetch(authLink.dataset.logoutUrl, {
        method: "POST",
        headers: { "X-CSRFToken": getCsrfToken() },
      });

      if (!response.ok) {
        throw new Error(`Logout failed with HTTP ${response.status}.`);
      }

      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      showSignedOutUser();
      window.stationeryNavigate(authLink.dataset.loginPage, { reload: true });
    } catch (error) {
      console.error("Unable to sign out.", error);
      alert(`${error.message} Please try again.`);
    }
  });

  async function showAuthenticatedUser() {
    if (!authLink) return;

    const requestId = ++authStateRequest;

    try {
      const response = await window.stationeryApiFetch(
        authLink.dataset.profileUrl,
      );

      if (response.status === 401) {
        if (requestId === authStateRequest) {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          showSignedOutUser();
        }
        return;
      }
      if (!response.ok) {
        throw new Error(`Could not load profile: ${response.status}`);
      }

      const user = await window.stationeryApiJson(
        response,
        "Could not load profile.",
      );
      if (requestId !== authStateRequest) return;

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

  document.addEventListener("turbo:load", showAuthenticatedUser);
  showAuthenticatedUser();
})();
