/* global bootstrap */
/// <reference lib="dom" />



document.addEventListener('DOMContentLoaded', function() {
    // Focus on the "Add Purchase" button when the page loads
    var addButton = document.getElementById('add-purchase-btn');
    if (addButton) {
        addButton.focus();
    }
    
    // Initialize Bootstrap dropdowns (modern and error-free)
    if (typeof bootstrap !== 'undefined') {
        var dropdownElementList = Array.from(document.querySelectorAll('.dropdown-toggle'));
        var dropdownList = dropdownElementList.map(function (el) {
            return new bootstrap.Dropdown(el);
        });
    }

    // Burger menu for mobile nav
    const burger = document.getElementById('burger');
    const navLinks = document.getElementById('nav-links');

    if (burger && navLinks) {
        burger.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }
});
