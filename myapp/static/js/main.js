/* Tab Switching Logic */
const tablinks = document.querySelectorAll(".tab-links");
const tabcontents = document.querySelectorAll(".tab-contents");

function opentab(tabname) {
    tablinks.forEach(tab => tab.classList.remove("active-link"));
    tabcontents.forEach(content => content.classList.remove("active-tab"));

    event.currentTarget.classList.add("active-link");
    document.getElementById(tabname).classList.add("active-tab");
}

/* Side Menu Control */
const sidemenu = document.getElementById("sidemenu");
function openmenu() {
    sidemenu.style.right = "0";
}
function closemenu() {
    sidemenu.style.right = "-200px";
}

/* Theme Toggle */
const toggleButton = document.getElementById("theme-toggle");

toggleButton.addEventListener("click", () => {
    document.body.classList.toggle("light-mode");

    // Update Toggle Icon
    toggleButton.textContent = document.body.classList.contains("light-mode")
        ? "🌞" // Sun icon
        : "🌙"; // Moon icon
});

/* Hide Navbar on Scroll Down */
let lastScrollTop = 0;
const navbar = document.querySelector("nav");

window.addEventListener("scroll", () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    navbar.style.top = scrollTop > lastScrollTop ? "-100px" : "0";
    lastScrollTop = scrollTop;
});

/* Typing Effect */
new Typed(".typing", {
    strings: ["Python Developer", "Web Developer", "AI/ML Researcher", "Data Scientist"],
    typeSpeed: 100,
    backSpeed: 60,
    loop: true
});
