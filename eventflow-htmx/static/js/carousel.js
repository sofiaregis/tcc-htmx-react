document.addEventListener("DOMContentLoaded", () => {
  const carousels = document.querySelectorAll(".carousel-wrapper");

  carousels.forEach((wrapper) => {
    const container = wrapper.querySelector(".carousel-container");
    const arrowLeft = wrapper.querySelector(".carousel-arrow.left");
    const arrowRight = wrapper.querySelector(".carousel-arrow.right");

    if (!container) return;

    // JavaScript is active: hide the default scrollbar to show the premium navigation arrows instead
    container.classList.add("hide-scrollbar");

    // Check if the container is scrollable to show arrows and center content if not
    const checkScrollable = () => {
      const isScrollable = container.scrollWidth > container.clientWidth;

      if (isScrollable) {
        container.classList.remove("center-content");
        if (arrowLeft && arrowRight) {
          arrowLeft.style.display = "flex";
          arrowRight.style.display = "flex";
        }
      } else {
        container.classList.add("center-content");
        if (arrowLeft && arrowRight) {
          arrowLeft.style.display = "none";
          arrowRight.style.display = "none";
        }
      }
    };

    // Run check initially and on resize
    setTimeout(checkScrollable, 50);
    window.addEventListener("resize", checkScrollable);

    // Simple progressive enhancement smooth scroll
    if (arrowLeft) {
      arrowLeft.addEventListener("click", () => {
        container.scrollBy({ left: -300, behavior: "smooth" });
      });
    }

    if (arrowRight) {
      arrowRight.addEventListener("click", () => {
        container.scrollBy({ left: 300, behavior: "smooth" });
      });
    }
  });
});
