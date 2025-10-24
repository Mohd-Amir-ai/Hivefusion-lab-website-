/*!
 * HiveFusion Lab - logic scripts
 * Copyright © 2025 HiveFusion Lab.
 * License: Proprietary
 * Unauthorized use is prohibited.
 * Author: HiveFusion Lab Team
 * Website: https://www.hivefusion.in
 */

"use strict";


function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === 'csrftoken=') {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}

async function handleSignup(event) {
    event.preventDefault();

    const uname = document.getElementById('uname')?.value.trim();
    const email = document.getElementById('email')?.value.trim();
    const password = document.getElementById('password')?.value;
    const confirmPassword = document.getElementById('confirm_password')?.value;

    if (!email || !password || !confirmPassword || !uname) {
        alert('Please fill in all fields.');
        return;
    }

    if(uname.length < 0){
        alert('kya dikkat hai bhai')
    }
    if (password !== confirmPassword) {
        alert('Passwords do not match.');
        return;
    }

    try {
        const response = await fetch(window.location.href, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({
                name : uname,
                email: email,
                password: password,
                confirm_password: confirmPassword,
            }),
        });

        const data = await response.json();

        if (response.ok) {
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            } else {
                alert('Signup successful! Redirecting...');
                window.location.href = '/';
            }
        } else {
            alert(data.message || 'Signup failed. Please try again.');
        }
    } catch (error) {
        console.error('Signup error:', error);
        alert('A network error occurred. Please try again.');
    }
}

