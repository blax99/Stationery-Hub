

document.addEventListener("DOMContentLoaded", function () {
    // Product Detail - Add to Cart
const productAddToCartButtons = document.querySelectorAll(".product-add-to-cart");

productAddToCartButtons.forEach((button) => {
    button.closest("form").addEventListener("submit", async function (event) {
        event.preventDefault();

        const token = localStorage.getItem("access_token");

        

        if (!token) {
            window.location.href = "/users/login-page/";
            return;
        }

        const productId = button.dataset.productId;
        const form = button.closest("form");
        const quantityInput = form.querySelector("#quantity");
        const quantity = Number(quantityInput.value);
        const maxQuantity = Number(quantityInput.max);

        if (!quantity || quantity < 1) {
            alert("Please enter a valid quantity.");
            return;
        }

        if (quantity > maxQuantity) {
            alert(`Only ${maxQuantity} items are available.`);
            return;
        }

        const originalButtonHTML = button.innerHTML;

        button.disabled = true;
        button.innerHTML = "Adding...";

        try {
            const response = await fetch("/cart/items/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: quantity
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || data.message || "Failed to add product to cart.");
            }

            button.innerHTML = "Added to Cart";

            updateCartCount();

            setTimeout(() => {
                button.innerHTML = originalButtonHTML;
                button.disabled = false;
            }, 1200);

        } catch (error) {
            console.error("Add to cart error:", error);

            alert(error.message);

            button.innerHTML = originalButtonHTML;
            button.disabled = false;
        }
    });
});

    // =========================
    // MOBILE MENU
    // =========================

    const menuBtn = document.getElementById("menu-btn");
    const mobileMenu = document.getElementById("mobile-menu");

    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener("click", function () {
            mobileMenu.classList.toggle("hidden");
        });
    }


    // =========================
    // CART
    // =========================

    const cartItems = document.querySelectorAll(".cart-item");
    const subtotalElement = document.getElementById("subtotal");
    const totalElement = document.getElementById("total");
    const summaryPrices = document.querySelectorAll(".summary-price");


    function updateCartTotal() {

        let subtotal = 0;

        cartItems.forEach(function (item, index) {

            const price = Number(item.dataset.price);

            const quantityElement = item.querySelector(".quantity");

            if (!quantityElement) {
                return;
            }

            const quantity = Number(
                quantityElement.textContent.trim()
            );

            const itemTotal = price * quantity;

            subtotal += itemTotal;

            const priceElement = item.querySelector(".price");

            if (priceElement) {
                priceElement.textContent =
                    "$" + itemTotal.toFixed(2);
            }

            if (summaryPrices[index]) {
                summaryPrices[index].textContent =
                    "$" + itemTotal.toFixed(2);
            }
        });


        if (subtotalElement) {
            subtotalElement.textContent =
                "$" + subtotal.toFixed(2);
        }

        if (totalElement) {
            totalElement.textContent =
                "$" + subtotal.toFixed(2);
        }
    }


   // =========================
// UPDATE CART QUANTITY
// =========================

const csrfToken = document.querySelector(
    "#cart-csrf-form input[name=csrfmiddlewaretoken]"
)?.value;

function updateCartQuantity(cartItem, quantity) {

    const itemId = cartItem.dataset.itemId;
    const updateUrl = cartItem.dataset.updateUrl;

    fetch(updateUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrfToken
        },
        body: `quantity=${quantity}`
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to update cart");
        }

        return response.text();
    })
    .then(() => {
        console.log(
            "Cart updated:",
            itemId,
            "Quantity:",
            quantity
        );

        updateCartCount();
    })
    .catch(error => {
        console.error(error);
    });
}


// =========================
// INCREASE QUANTITY
// =========================

const increaseButtons =
    document.querySelectorAll(".increase");

increaseButtons.forEach(function (button) {
    button.addEventListener("click", function () {
        const cartItem =
            button.closest(".cart-item");

        const quantityElement =
            cartItem.querySelector(".quantity");

        let quantity =
            Number(quantityElement.textContent.trim());

        const stock =
            Number(cartItem.dataset.stock);

        if (quantity >= stock) {
            return;
        }

        quantity++;

        quantityElement.textContent = quantity;

        updateCartTotal();

        updateCartQuantity(
            cartItem,
            quantity
        );
    });
});

// =========================
// DECREASE QUANTITY
// =========================

const decreaseButtons =
    document.querySelectorAll(".decrease");

decreaseButtons.forEach(function (button) {

    button.addEventListener("click", function () {

        const cartItem =
            button.closest(".cart-item");

        const quantityElement =
            cartItem.querySelector(".quantity");

        let quantity =
            Number(quantityElement.textContent.trim());

        if (quantity > 1) {
            quantity--;

            quantityElement.textContent = quantity;

            updateCartTotal();

            updateCartQuantity(
                cartItem,
                quantity
            );
        }
    });
});

    // =========================
    // CART DELETE
    // =========================

    const deleteButtons =
    document.querySelectorAll(".delete");

deleteButtons.forEach(function (button) {
    button.addEventListener("click", function () {

        const cartItem =
            button.closest(".cart-item");

        const deleteUrl =
            button.dataset.deleteUrl;

        if (!cartItem || !deleteUrl) {
            return;
        }

        fetch(deleteUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken
            }
        })
        .then(response => {

            if (!response.ok) {
                throw new Error("Failed to delete cart item");
            }

            cartItem.remove();
            updateCartTotal();
            updateCartCount();

        })
        .catch(error => {
            console.error(error);
        });
    });
});


        // =========================
    // WISHLIST
    // =========================

    const wishlistButtons =
        document.querySelectorAll(".wishlist-btn");

    if (wishlistButtons.length > 0) {

        const wishlistMap = new Map();

        function setWishlistActive(button) {

            button.classList.remove("text-gray-400");
            button.classList.add("text-red-500");

            const svg = button.querySelector("svg");

            if (svg) {
                svg.setAttribute("fill", "currentColor");
                svg.setAttribute("stroke", "currentColor");
            }

            button.title = "Remove from Wishlist";
        }

        function setWishlistInactive(button) {

            button.classList.remove("text-red-500");
            button.classList.add("text-gray-400");

            const svg = button.querySelector("svg");

            if (svg) {
                svg.setAttribute("fill", "none");
                svg.setAttribute("stroke", "currentColor");
            }

            button.title = "Add to Wishlist";
        }

        async function loadWishlistStatus() {

            const token =
                localStorage.getItem("access_token");

            if (!token) {

                wishlistButtons.forEach(function (button) {
                    setWishlistInactive(button);
                });

                return;
            }

            try {

                const response = await fetch(
                    "/wishlist/api/",
                    {
                        method: "GET",
                        headers: {
                            "Authorization":
                                `Bearer ${token}`
                        }
                    }
                );

                const data =
                    await response.json();

                if (!response.ok) {
                    return;
                }

                wishlistMap.clear();

                data.items.forEach(function (item) {

                    wishlistMap.set(
                        String(item.product_id),
                        item.id
                    );
                });

                wishlistButtons.forEach(function (button) {

                    const productId =
                        String(button.dataset.productId);

                    if (wishlistMap.has(productId)) {
                        setWishlistActive(button);
                    } else {
                        setWishlistInactive(button);
                    }
                });

            } catch (error) {

                console.error(
                    "Error loading wishlist:",
                    error
                );
            }
        }

        wishlistButtons.forEach(function (button) {

            button.addEventListener(
                "click",
                async function () {

                    const token =
                        localStorage.getItem("access_token");
                        

                    if (!token) {
                        

                        window.location.href =
                            "/users/login-page/";

                        return;
                    }

                    const productId =
                        String(this.dataset.productId);

                    const wishlistItemId =
                        wishlistMap.get(productId);

                    this.disabled = true;

                    try {

                        // =========================
                        // REMOVE FROM WISHLIST
                        // =========================

                        if (wishlistItemId) {

                            const response =
                                await fetch(
                                    "/wishlist/api/",
                                    {
                                        method: "DELETE",
                                        headers: {
                                            "Content-Type":
                                                "application/json",
                                            "Authorization":
                                                `Bearer ${token}`
                                        },
                                        body: JSON.stringify({
                                            item_id:
                                                wishlistItemId
                                        })
                                    }
                                );

                            const data =
                                await response.json();

                            if (
                                response.ok &&
                                data.success
                            ) {

                                wishlistMap.delete(
                                    productId
                                );

                                setWishlistInactive(
                                    this
                                );

                                if (
                                    typeof updateWishlistNavCount ===
                                    "function"
                                ) {
                                    await updateWishlistNavCount();
                                }

                            } else {

                                alert(
                                    data.error ||
                                    data.message ||
                                    "Unable to remove product from wishlist."
                                );
                            }

                        }

                        // =========================
                        // ADD TO WISHLIST
                        // =========================

                        else {

                            const response =
                                await fetch(
                                    "/wishlist/api/",
                                    {
                                        method: "POST",
                                        headers: {
                                            "Content-Type":
                                                "application/json",
                                            "Authorization":
                                                `Bearer ${token}`
                                        },
                                        body: JSON.stringify({
                                            product_id:
                                                productId
                                        })
                                    }
                                );

                            const data =
                                await response.json();

                            if (
                                response.ok &&
                                data.success
                            ) {

                                if (
                                    data.wishlist_item_id
                                ) {

                                    wishlistMap.set(
                                        productId,
                                        data.wishlist_item_id
                                    );
                                }

                                setWishlistActive(
                                    this
                                );

                                if (
                                    typeof updateWishlistNavCount ===
                                    "function"
                                ) {
                                    await updateWishlistNavCount();
                                }

                            } else {

                                alert(
                                    data.error ||
                                    data.message ||
                                    "Unable to add product to wishlist."
                                );
                            }
                        }

                    } catch (error) {

                        console.error(
                            "Wishlist request error:",
                            error
                        );

                        alert(
                            "Unable to update wishlist."
                        );

                    } finally {

                        this.disabled = false;
                    }
                }
            );
        });

        loadWishlistStatus();
    }

});

function updateCartCount() {
    const cartCount = document.getElementById("cart-count");

    if (!cartCount) {
        return;
    }

    const accessToken = localStorage.getItem("access_token");

    if (!accessToken) {
        cartCount.textContent = "0";
        return;
    }

    fetch("/cart/items/", {
        headers: {
            Authorization: `Bearer ${accessToken}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to fetch cart");
        }

        return response.json();
    })
    .then(data => {
        const totalQuantity = data.items.reduce(
            (total, item) => total + Number(item.quantity),
            0
        );

        cartCount.textContent = totalQuantity;
    })
    .catch(error => {
        console.error("Cart count error:", error);
        cartCount.textContent = "0";
    });
}

updateCartCount();

function updateWishlistNavCount() {
    const wishlistNavCount =
        document.getElementById("wishlist-nav-count");

    if (!wishlistNavCount) {
        return;
    }

    const accessToken =
        localStorage.getItem("access_token");

    if (!accessToken) {
        wishlistNavCount.textContent = "0";
        return;
    }

    fetch("/wishlist/api/", {
        headers: {
            Authorization: `Bearer ${accessToken}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to fetch wishlist");
        }

        return response.json();
    })
    .then(data => {
        wishlistNavCount.textContent =
            data.items.length;
    })
    .catch(error => {
        console.error(
            "Wishlist count error:",
            error
        );

        wishlistNavCount.textContent = "0";
    });
}

updateWishlistNavCount();



