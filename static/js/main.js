console.log("MAIN JS IS WORKING");

document.addEventListener("DOMContentLoaded", function () {

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

            quantity++;

            quantityElement.textContent = quantity;

            updateCartTotal();
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
            }

            quantityElement.textContent = quantity;

            updateCartTotal();
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

            if (cartItem) {
                cartItem.remove();
                updateCartTotal();
            }
        });
    });


    updateCartTotal();


    // =========================
    // WISHLIST
    // =========================

    const wishlistItemsContainer =
        document.getElementById("wishlist-items");

    const wishlistCount =
        document.getElementById("wishlist-count");

    const emptyWishlist =
        document.getElementById("empty-wishlist");


    if (wishlistItemsContainer) {

        let wishlistItems =
            JSON.parse(
                localStorage.getItem("wishlistItems")
            );


        // First time opening wishlist
        if (!wishlistItems) {

            wishlistItems = [];

            document
                .querySelectorAll(".wishlist-item")
                .forEach(function (item) {

                    const productName =
                        item.querySelector("h2").textContent.trim();

                    wishlistItems.push(productName);
                });

            localStorage.setItem(
                "wishlistItems",
                JSON.stringify(wishlistItems)
            );
        }


        // =========================
        // REMOVE WISHLIST ITEM
        // =========================

        function removeFromWishlist(item) {

            const productName =
                item.querySelector("h2").textContent.trim();

            wishlistItems =
                wishlistItems.filter(function (name) {
                    return name !== productName;
                });

            localStorage.setItem(
                "wishlistItems",
                JSON.stringify(wishlistItems)
            );

            item.remove();

            updateWishlistUI();
        }


        // =========================
        // UPDATE WISHLIST UI
        // =========================

        function updateWishlistUI() {

            const remainingItems =
                wishlistItemsContainer.querySelectorAll(
                    ".wishlist-item"
                );

            if (wishlistCount) {

                wishlistCount.textContent =
                    remainingItems.length +
                    (remainingItems.length === 1
                        ? " item"
                        : " items");
            }


            if (remainingItems.length === 0) {

                if (emptyWishlist) {
                    emptyWishlist.classList.remove("hidden");
                }

            } else {

                if (emptyWishlist) {
                    emptyWishlist.classList.add("hidden");
                }
            }
        }


        // =========================
        // RESTORE WISHLIST
        // =========================

        document
            .querySelectorAll(".wishlist-item")
            .forEach(function (item) {

                const productName =
                    item.querySelector("h2").textContent.trim();

                if (!wishlistItems.includes(productName)) {
                    item.remove();
                }
            });


        // =========================
        // REMOVE BUTTONS
        // =========================

        document
            .querySelectorAll(".remove-wishlist")
            .forEach(function (button) {

                button.addEventListener("click", function () {

                    const item =
                        button.closest(".wishlist-item");

                    if (item) {
                        removeFromWishlist(item);
                    }
                });
            });


        // =========================
        // ADD TO CART BUTTONS
        // =========================

        document
            .querySelectorAll(".add-to-cart")
            .forEach(function (button) {

                button.addEventListener("click", function () {

                    button.textContent = "Added to Cart";

                    button.classList.add("opacity-70");

                    button.disabled = true;


                    setTimeout(function () {

                        button.textContent = "Add to Cart";

                        button.classList.remove("opacity-70");

                        button.disabled = false;

                    }, 1500);
                });
            });


        updateWishlistUI();
    }

});