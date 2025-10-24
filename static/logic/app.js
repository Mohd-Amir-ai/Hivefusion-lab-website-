/*!
 * HiveFusion Lab - Frontend Scripts
 * Copyright © 2025 HiveFusion Lab.
 * License: Proprietary
 * Unauthorized use is prohibited.
 * Author: HiveFusion Lab Team
 * Website: https://www.hivefusion.in
 */

const mainImage = document.getElementById('pocket-mini-main-image');
const thumbnails = document.querySelectorAll('.product__pocket__mini__thumbnail');
const counters = document.querySelectorAll('.count');
const hamburger = document.querySelector('.show--mobile');
const mobileMenu = document.querySelector('.mobile-menu');
const closeBtn = document.getElementById('closeMenu');
const ContactHome = document.getElementById('contact-form')

hamburger.addEventListener('click', () => {
    mobileMenu.classList.remove('hidden');
    document.body.classList.add('menu-open');
});

closeBtn.addEventListener('click', () => {
    mobileMenu.classList.add('hidden');
    document.body.classList.remove('menu-open');
});

thumbnails.forEach(thumb => {
    thumb.addEventListener('click', () => {
        const newSrc = thumb.dataset.full;
        mainImage.style.opacity = 0;
        setTimeout(() => {
            mainImage.src = newSrc;
            mainImage.alt = thumb.alt;
            mainImage.style.opacity = 1;
        }, 200);
    });
});


const animateCount = (el) => {
    const target = +el.getAttribute('data-target');
    let current = 0;

    const update = () => {
        const step = Math.ceil(target / 60); // Smoothness
        current += step;

        if (current >= target) {
            el.textContent = target + '%';
        } else {
            el.textContent = current + '%';
            requestAnimationFrame(update);
        }
    };

    update();
};

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateCount(entry.target);
            observer.unobserve(entry.target); // Run once
        }
    });
}, { threshold: 0.9 });

counters.forEach(counter => {
    observer.observe(counter);
});

ContactHome.addEventListener('submit', function (e) {
    e.preventDefault(); 

    const form = e.target;
    const formData = new FormData(form);

    fetch("", {
        method: "POST",
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('response-msg').innerText = data.message;
            form.reset();
        })
        .catch(error => {
            document.getElementById('response-msg').innerText = "Something went wrong.";
        });
});

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


function joinin() {
    const Joinemail = document.getElementById('Join-email').value.trim();
    const csrftoken = getCookie("csrftoken");
    if (!Joinemail) {
        alert("Email field cannot be empty.");
        return;
    }

    fetch("/join", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken, 
        },
        body: JSON.stringify({ email: Joinemail }),
    })
    .then(response => {
        if (!response.ok) throw new Error("Network response was not ok");
        return response.json();
    })
    .then(data => {
        console.log(data);
        alert("You’ve successfully subscribed!");
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Something went wrong. Please try again.");
    });
}
