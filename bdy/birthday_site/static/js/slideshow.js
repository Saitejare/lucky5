const slides = document.querySelectorAll(".slide");
const nextBtn = document.getElementById("nextBtn");
const prevBtn = document.getElementById("prevBtn");
let currentIndex = 0;

function showSlide(index) {
    slides.forEach((slide, position) => {
        slide.classList.toggle("active", position === index);
    });
}

function nextSlide() {
    currentIndex = (currentIndex + 1) % slides.length;
    showSlide(currentIndex);
}

function previousSlide() {
    currentIndex = (currentIndex - 1 + slides.length) % slides.length;
    showSlide(currentIndex);
}

if (slides.length > 0) {
    showSlide(currentIndex);
    setInterval(nextSlide, 4000);
}

if (nextBtn) {
    nextBtn.addEventListener("click", nextSlide);
}

if (prevBtn) {
    prevBtn.addEventListener("click", previousSlide);
}
