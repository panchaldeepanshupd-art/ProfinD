/**
 * ProfinD — Client-Side JavaScript
 * Handles navigation interactions and form validations
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Mobile Navigation Menu Toggle
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function () {
            navMenu.classList.toggle('active');
        });
    }

    // 2. Search Form Validation
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');

    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', function (event) {
            const query = searchInput.value.trim();

            if (!query) {
                event.preventDefault();
                alert('Please enter a product name or keyword to search.');
                searchInput.focus();
            }
        });
    }
});
