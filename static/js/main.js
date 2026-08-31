console.log("MAIN JS IS WORKING");

document.addEventListener("DOMContentLoaded", function () {

    const menuBtn = document.getElementById("menu-btn");
    const mobileMenu = document.getElementById("mobile-menu");

    if (menuBtn && mobileMenu) {

        menuBtn.addEventListener("click", function () {
            mobileMenu.classList.toggle("hidden");
        });

    }


    const subtotalElement = document.getElementById("subtotal");
    const totalElement = document.getElementById("total");


    function updateCartTotal() {

        const cartItems =
            document.querySelectorAll(".cart-item");

        const summaryPrices =
            document.querySelectorAll(".summary-price");

        let subtotal = 0;


        cartItems.forEach(function (item, index) {

            const price =
                Number(item.dataset.price);

            const quantityElement =
                item.querySelector(".quantity");

            const quantity =
                Number(quantityElement.textContent.trim());

            const itemTotal =
                price * quantity;

            subtotal += itemTotal;


            const priceElement =
                item.querySelector(".price");

            priceElement.textContent =
                "$" + itemTotal.toFixed(2);


            if (summaryPrices[index]) {

                summaryPrices[index].textContent =
                    "$" + itemTotal.toFixed(2);

            }

        });


        subtotalElement.textContent =
            "$" + subtotal.toFixed(2);

        totalElement.textContent =
            "$" + subtotal.toFixed(2);

    }


    const increaseButtons =
        document.querySelectorAll(".increase");


    const decreaseButtons =
        document.querySelectorAll(".decrease");


    increaseButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const cartItem =
                button.closest(".cart-item");

            const quantityElement =
                cartItem.querySelector(".quantity");

            let quantity =
                Number(quantityElement.textContent.trim());

            quantity++;

            quantityElement.textContent =
                quantity;

            updateCartTotal();

        });

    });


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

            quantityElement.textContent =
                quantity;

            updateCartTotal();

        });

    });


    const deleteButtons =
        document.querySelectorAll(".delete");


    deleteButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const cartItem =
                button.closest(".cart-item");

            const cartItems =
                document.querySelectorAll(".cart-item");

            const summaryItems =
                document.querySelectorAll(".summary-item");

            const index =
                Array.from(cartItems).indexOf(cartItem);


            cartItem.remove();


            if (summaryItems[index]) {

                summaryItems[index].remove();

            }


            updateCartTotal();

        });

    });


    updateCartTotal();

});

