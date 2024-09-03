document.addEventListener("DOMContentLoaded", function () {
    // Get all navigation links and pages
    const navLinks = document.querySelectorAll(".nav-item");
    const pages = document.querySelectorAll(".page");
    console.log(pages);

    // Add click event listener to each nav link
    navLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault(); // Prevent default anchor click behavior
            // Get the target page from data-target attribute
            const targetPage = this.getAttribute("data-target");
            // Hide all pages
            pages.forEach(page => {
                page.classList.remove("active");
            });

            // Show the selected page
            const selectedPage = document.getElementById(targetPage);
            selectedPage.classList.add("active");
        });
    });
});
