
    document.addEventListener('DOMContentLoaded', function() {
        // Focus on the "Add Purchase" button when the page loads
        var addButton = document.getElementById('add-purchase-btn');
        if (addButton) {
            addButton.focus();
        }
    });


    const burger = document.getElementById('burger');
    const navLinks = document.getElementById('nav-links');

    burger.addEventListener('click', () => {
        navLinks.classList.toggle('active'); // Toggle the active class
    });