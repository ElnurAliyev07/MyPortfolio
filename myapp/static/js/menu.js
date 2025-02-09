document.addEventListener('DOMContentLoaded', function() {
    const sidemenu = document.getElementById('sidemenu');
    const menuOpen = document.getElementById('menu-open');
    const menuClose = document.getElementById('menu-close');

    function toggleMenu() {
        sidemenu.classList.toggle('active');
        menuOpen.style.display = sidemenu.classList.contains('active') ? 'none' : 'block';
        menuClose.style.display = sidemenu.classList.contains('active') ? 'block' : 'none';
    }

    menuOpen.addEventListener('click', toggleMenu);
    menuClose.addEventListener('click', toggleMenu);

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        const isClickInside = sidemenu.contains(event.target) ||
                              menuOpen.contains(event.target) ||
                              menuClose.contains(event.target);

        if (!isClickInside && sidemenu.classList.contains('active')) {
            toggleMenu();
        }
    });

    // Close menu when resizing to larger screen
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768 && sidemenu.classList.contains('active')) {
            toggleMenu();
        }
    });
});

