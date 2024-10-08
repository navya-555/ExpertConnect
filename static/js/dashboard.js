document.addEventListener("DOMContentLoaded", function () {
    // Get all navigation links and pages
    const navLinks = document.querySelectorAll(".nav-item");
    const pages = document.querySelectorAll(".page");
    const nav = document.querySelector("nav");
    const navItemTitles = document.querySelectorAll(".nav-item-title");
    const formSectionChanger = document.getElementById('form-section-changer');
    const expertRegistrationForm = document.getElementById('expert-registration-form');
    const formSections = expertRegistrationForm.querySelectorAll('.form-section');
    const form = document.getElementById('expert-registration-form');

    let form_section_count = 0;

    // Add click event listener to each nav link
    navLinks.forEach((link, index) => {
        // Check if it's not the last item
        if (index !== navLinks.length - 1) {
            link.addEventListener("click", function (e) {
                e.preventDefault(); // Prevent default anchor click behavior

                //adding styles for active nav item
                navLinks.forEach(link => {
                    link.classList.remove('active-nav-item');
                });
                this.classList.add('active-nav-item');

                // Get the target page from the data-target attribute
                const targetPage = this.getAttribute("data-target");

                // Hide all pages
                pages.forEach(page => {
                    page.classList.remove("active");
                });

                // Show the selected page
                const selectedPage = document.getElementById(targetPage);
                console.log(selectedPage);
                selectedPage.classList.add("active");
            });
        }
    });
    nav.addEventListener('mouseenter', () => {
        nav.classList.add('expanded');
        navItemTitles.forEach(title => {
            title.style.display = 'block';
        });
    });

    nav.addEventListener('mouseleave', () => {
        nav.classList.remove('expanded');
        navItemTitles.forEach(title => {
            title.style.display = 'none';
        });
    });

    formSectionChanger.addEventListener('click', (e) => {
        e.preventDefault();
        console.log('clicked', form_section_count);

        // Get all required inputs in the current section
        // const currentSection = formSections[form_section_count];

        // Validate the fields
        // let allValid = true;
        // console.log(requiredFields);
        // requiredFields.forEach(input => {
        //     if (!input.value) {
        //         allValid = false;
        //         input.classList.add('error'); // Add an error class if empty
        //     } else {
        //         input.classList.remove('error'); // Remove error if valid
        //     }
        // });

        // If all fields are valid, go to the next section
        // If it's the last section, change button to "Submit"
        console.log(form_section_count, formSections.length - 1)
        console.log(formSections);
        if (form_section_count === formSections.length - 1) {
            // Submit the form
            form.submit();
        } else {
            // Go to the next section
            formSections[form_section_count].classList.remove('active');
            form_section_count++;
            formSections[form_section_count].classList.add('active');

            // Check if we are on the last section now
            if (form_section_count === formSections.length - 1) {
                formSectionChanger.textContent = "Submit";
            }
        }

    });

});
