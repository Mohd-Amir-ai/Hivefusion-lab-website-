
// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== "") {
//         const cookies = document.cookie.split(";");
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             // Match cookie name
//             if (cookie.startsWith(name + "=")) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }

// async function addToCart(p_code, quantity , idbtn) {
//     const loginStatusURL = "http://localhost:8000/f8e7b3a1/";
//     const cartUpdateURL = "http://localhost:8000/product/up-crt";
//     const csrftoken = getCookie("csrftoken");
//     const sessionid = getCookie("sessionid");
//     const btnux = document.getElementById(idbtn)
//     try {

//         const loginRes = await fetch(loginStatusURL, {
//             method: "GET",
//             credentials: "include"
//         });

//         if (!loginRes.ok) throw new Error("Login status check failed.");
//         const loginData = await loginRes.json();

//         if (!loginData.ls) {
//             alert("Please login to add items to cart.");
//             return;
//         }

//         // Step 2: Send POST request to update cart
//         const res = await fetch(cartUpdateURL, {
//             method: "POST",
//             credentials: "include",
//             headers: {
//                 "Content-Type": "application/json",
//                 "X-CSRFToken": csrftoken
//             },
//             body: JSON.stringify({
//                 p_code: p_code,
//                 qty: quantity
//             })
//         });

//         if (!res.ok) {
//             const errorData = await res.json();
//             console.error("Cart update error:", errorData);
//             alert("Failed to add item to cart. Please try again.");
//             return;
//         }

//         const result = await res.json();
//         console.log("Cart update success:", result);
//         btnux.innerText = 'Added'
//     } catch (err) {
//         console.error("Add to cart error:", err);
//         alert("An unexpected error occurred. Please try again.");
//     }
// }

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function addToCart(p_code, quantity, idbtn) {
    const loginStatusURL = "http://localhost:8000/f8e7b3a1/";
    const cartUpdateURL = "http://localhost:8000/product/up-crt";
    const csrftoken = getCookie("csrftoken");
    const sessionid = getCookie("sessionid");
    const btnux = document.getElementById(idbtn);

    // Store original content
    const originalHTML = btnux.innerHTML;

    try {
        // UX: Show loading state
        btnux.disabled = true;
        btnux.innerHTML = 'Adding... <span class="rotating-cart"></span>';

        const loginRes = await fetch(loginStatusURL, {
            method: "GET",
            credentials: "include"
        });

        if (!loginRes.ok) throw new Error("Login status check failed.");
        const loginData = await loginRes.json();

        if (!loginData.ls) {
            alert("Please login to add items to cart.");
            btnux.disabled = false;
            btnux.innerHTML = originalHTML;
            return;
        }

        const res = await fetch(cartUpdateURL, {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({
                p_code: p_code,
                qty: quantity
            })
        });

        if (!res.ok) {
            const errorData = await res.json();
            console.error("Cart update error:", errorData);
            alert("Failed to add item to cart.");
            btnux.disabled = false;
            btnux.innerHTML = originalHTML;
            return;
        }

        const result = await res.json();

        btnux.innerHTML = 'Added ✓';
        setTimeout(() => {
            btnux.disabled = false;
            btnux.innerHTML = originalHTML;
        }, 1000);

    } catch (err) {
        console.error("Add to cart error:", err);
        alert("An unexpected error occurred.");
        btnux.disabled = false;
        btnux.innerHTML = originalHTML;
    }
}


document.addEventListener("DOMContentLoaded", () => {
    const csrftoken = getCookie("csrftoken");
    const sessionid = getCookie("sessionid");

    fetch("/product/down-crt", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
            "X-SessionID": sessionid
        },
        body: JSON.stringify({})
    })
    .then(response => {
        if (!response.ok) throw new Error("Network response was not ok");
        return response.json();
    })
    .then(data => {
        const container = document.getElementById("cartContainer");
        container.innerHTML = ""; // Clear previous content

        data.data.forEach(item => {
            const cartRow = document.createElement("div");
            cartRow.classList.add("cart__row");

            cartRow.innerHTML = `
                <div class="cart__item px-10">
                    <img src="${item.image_url}" alt="${item.product}" />
                    <div>
                        <h3>${item.product}</h3>
                        <p class="cart__stock">Low stock only<br>few left</p>
                    </div>
                </div>
                <div>
                    <p class="hidden show--mobile">Price</p>${item.price}₹
                </div>
                <div class="cart__qty">
                    <button>+</button>
                    <span>${item.qty}</span>
                    <button>-</button>
                </div>
                <div>
                    <p class="hidden show--mobile">Subtotal</p>${item.price * item.qty}₹
                </div>
            `;

            container.appendChild(cartRow);
        });
    })
    .catch(error => {
        console.error("Error fetching cart data:", error);
    });
});

