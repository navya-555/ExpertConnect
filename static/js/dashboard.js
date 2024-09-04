document.addEventListener("DOMContentLoaded", function () {
    // Get all navigation links and pages
    const navLinks = document.querySelectorAll(".nav-item");
    const pages = document.querySelectorAll(".page");
    const nav = document.querySelector("nav");
    const navItemTitles = document.querySelectorAll(".nav-item-title");
    console.log(pages);

    // Add click event listener to each nav link
    navLinks.forEach((link, index) => {
        // Check if it's not the last item
        if (index !== navLinks.length - 1) {
            link.addEventListener("click", function (e) {
                e.preventDefault(); // Prevent default anchor click behavior

                // Get the target page from the data-target attribute
                const targetPage = this.getAttribute("data-target");

                // Hide all pages
                pages.forEach(page => {
                    page.classList.remove("active");
                });

                // Show the selected page
                const selectedPage = document.getElementById(targetPage);
                selectedPage.classList.add("active");
            });
        }
    });
    nav.addEventListener('mouseenter', () => {
        if (window.innerWidth <= 900) {
            nav.classList.add('expanded');
            navItemTitles.forEach(title => {
                title.style.display = 'block';
            });
        }
    });

    nav.addEventListener('mouseleave', () => {
        if(window.innerWidth <= 900) {
            nav.classList.remove('expanded');
            navItemTitles.forEach(title => {
                title.style.display = 'none';
            });
        }
    });
    window.addEventListener('resize', () => {
        if (window.innerWidth > 900) {
            nav.classList.remove('expanded');
            navItemTitles.forEach(title => {
                title.style.display = '';
            });
        } else {
            navItemTitles.forEach(title => {
                title.style.display = 'none';
            });
        }
    });

});
