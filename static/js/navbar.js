(() => {
  const navbar = document.getElementById("site-navbar");
  if (!navbar || navbar.dataset.navbarInitialized === "true") return;
  navbar.dataset.navbarInitialized = "true";

  const searchButton = document.getElementById("searchButton");
  const searchBox = document.getElementById("searchBox");
  const searchInput = document.getElementById("searchInput");
  const menuButton = document.getElementById("menuButton");
  const mobileMenu = document.getElementById("mobileMenu");
  const menuIcon = document.getElementById("menuIcon");
  const authLink = document.getElementById("authLink");
  const mobileAuthLink = document.getElementById("mobileAuthLink");
  const accountButton = document.getElementById("accountButton");
  const mobileAccountButton = document.getElementById("mobileAccountButton");
  const userDropdown = document.getElementById("userDropdown");
  const mobileUserDropdown = document.getElementById("mobileUserDropdown");
  const categoriesButton = document.getElementById("categoriesButton");
  const categoriesDropdown = document.getElementById("categoriesDropdown");
  const mobileCategoriesButton = document.getElementById(
    "mobileCategoriesButton",
  );
  const mobileCategoriesDropdown = document.getElementById(
    "mobileCategoriesDropdown",
  );
  let authStateRequest = 0;

  function setExpanded(button, dropdown, expanded, displayClass) {
    if (!button || !dropdown) return;

    button.setAttribute("aria-expanded", String(expanded));
    dropdown.classList.toggle("hidden", !expanded);
    if (displayClass) dropdown.classList.toggle(displayClass, expanded);
    const chevron = button.querySelector(".account-chevron");
    if (chevron) {
      chevron.style.transform = expanded ? "rotate(180deg)" : "";
    }
  }

  function closeDropdowns() {
    setExpanded(categoriesButton, categoriesDropdown, false);
    setExpanded(
      mobileCategoriesButton,
      mobileCategoriesDropdown,
      false,
      "flex",
    );
    setExpanded(accountButton, userDropdown, false);
    setExpanded(
      mobileAccountButton,
      mobileUserDropdown,
      false,
      "flex",
    );
  }

  function closeMobileMenu() {
    if (!mobileMenu || !menuIcon || !menuButton) return;

    mobileMenu.classList.add("hidden");
    menuIcon.classList.remove("fa-xmark");
    menuIcon.classList.add("fa-bars");
    menuButton.setAttribute("aria-expanded", "false");
    closeDropdowns();
  }

  function showSignedOutUser() {
    authStateRequest += 1;
    authLink.replaceChildren(document.createTextNode("Sign In"));
    authLink.href = authLink.dataset.loginPage;
    authLink.classList.remove("hidden");
    mobileAuthLink.classList.remove("hidden");
    accountButton.classList.add("hidden");
    mobileAccountButton.classList.add("hidden");
    closeDropdowns();
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

  function setAccountButton(button, username, initials) {
    button.querySelector(".account-avatar").textContent = initials;
    button.querySelector(".account-name").textContent = username;
    button.setAttribute("aria-label", `Account options for ${username}`);
  }

  searchButton?.addEventListener("click", () => {
    searchBox.classList.remove("hidden");
    searchButton.classList.add("hidden");
    searchInput.focus();
  });

  document.addEventListener("click", (event) => {
    const target = event.target;
    const clickedElement = target instanceof Element ? target : null;
    if (!clickedElement) return;

    if (
      searchBox &&
      searchButton &&
      !searchBox.contains(target) &&
      !searchButton.contains(target)
    ) {
      searchBox.classList.add("hidden");
      searchButton.classList.remove("hidden");
    }

    if (clickedElement.closest("#mobileMenu a")) {
      closeMobileMenu();
    }

    if (
      clickedElement.closest(
        "#categoriesDropdown a, #userDropdown a, #mobileCategoriesDropdown a, #mobileUserDropdown a",
      )
    ) {
      closeDropdowns();
    }

    if (
      !clickedElement.closest(
        "#categoriesButton, #categoriesDropdown, #mobileCategoriesButton, #mobileCategoriesDropdown, #accountButton, #userDropdown, #mobileAccountButton, #mobileUserDropdown",
      )
    ) {
      closeDropdowns();
    }
  });

  menuButton?.addEventListener("click", () => {
    const isOpen = mobileMenu.classList.contains("hidden");
    if (isOpen) {
      mobileMenu.classList.remove("hidden");
      menuIcon.classList.remove("fa-bars");
      menuIcon.classList.add("fa-xmark");
      menuButton.setAttribute("aria-expanded", "true");
    } else {
      closeMobileMenu();
    }
  });

  categoriesButton?.addEventListener("click", () => {
    const isExpanded = categoriesButton.getAttribute("aria-expanded") === "true";
    closeDropdowns();
    setExpanded(categoriesButton, categoriesDropdown, !isExpanded);
  });

  mobileCategoriesButton?.addEventListener("click", () => {
    const isExpanded =
      mobileCategoriesButton.getAttribute("aria-expanded") === "true";
    closeDropdowns();
    setExpanded(
      mobileCategoriesButton,
      mobileCategoriesDropdown,
      !isExpanded,
      "flex",
    );
  });

  accountButton?.addEventListener("click", () => {
    const isExpanded = accountButton.getAttribute("aria-expanded") === "true";
    closeDropdowns();
    setExpanded(accountButton, userDropdown, !isExpanded);
  });

  mobileAccountButton?.addEventListener("click", () => {
    const isExpanded =
      mobileAccountButton.getAttribute("aria-expanded") === "true";
    closeDropdowns();
    setExpanded(
      mobileAccountButton,
      mobileUserDropdown,
      !isExpanded,
      "flex",
    );
  });

  document.querySelectorAll(".logoutButton").forEach((button) => {
    button.addEventListener("click", async () => {
      closeMobileMenu();

      try {
        const headers = {};
        const csrfToken = getCsrfToken();
        if (csrfToken) headers["X-CSRFToken"] = csrfToken;

        const response = await fetch(authLink.dataset.logoutUrl, {
          method: "POST",
          headers,
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

      const username = user.username;
      const initials = username
        .split(/\s+/)
        .map((part) => part[0])
        .join("")
        .slice(0, 2)
        .toUpperCase();

      authLink.classList.add("hidden");
      mobileAuthLink.classList.add("hidden");
      accountButton.classList.remove("hidden");
      mobileAccountButton.classList.remove("hidden");
      accountButton.classList.add("inline-flex");
      mobileAccountButton.classList.add("flex");
      setAccountButton(accountButton, username, initials);
      setAccountButton(mobileAccountButton, username, initials);
    } catch (error) {
      console.error("Unable to display the signed-in user.", error);
    }
  }

  function resetNavigation() {
    closeMobileMenu();
    closeDropdowns();
  }

  document.addEventListener("turbo:before-cache", resetNavigation);
  document.addEventListener("turbo:load", () => {
    resetNavigation();
    showAuthenticatedUser();
  });

  resetNavigation();
  showAuthenticatedUser();
})();
