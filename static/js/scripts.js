
    document.addEventListener('DOMContentLoaded', function() {
        // Focus on the "Add Purchase" button when the page loads
        var addButton = document.getElementById('add-purchase-btn');
        if (addButton) {
            addButton.focus();
        }
        
        // Initialize Bootstrap dropdowns (though they should work automatically)
        var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
        var dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
            return new bootstrap.Dropdown(dropdownToggleEl);
        });
    });


    const burger = document.getElementById('burger');
    const navLinks = document.getElementById('nav-links');

    if (burger && navLinks) {
        burger.addEventListener('click', () => {
            navLinks.classList.toggle('active'); // Toggle the active class
        });
    }