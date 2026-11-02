import React, { useRef, useState, useEffect } from "react";

export default function Carousel({ children, showArrows = true }) {
  const containerRef = useRef(null);
  const [isScrollable, setIsScrollable] = useState(false);

  // Verifica se o conteúdo ultrapassa a largura do contêiner para exibir setas
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const checkScrollable = () => {
      setIsScrollable(container.scrollWidth > container.clientWidth);
    };

    // Executa após a renderização
    const timer = setTimeout(checkScrollable, 100);

    window.addEventListener("resize", checkScrollable);
    return () => {
      clearTimeout(timer);
      window.removeEventListener("resize", checkScrollable);
    };
  }, [children]);

  const scrollByAmount = (amount) => {
    const container = containerRef.current;
    if (container) {
      container.scrollBy({ left: amount, behavior: "smooth" });
    }
  };

  const handleNext = () => {
    scrollByAmount(300);
  };

  const handlePrev = () => {
    scrollByAmount(-300);
  };

  return (
    <div className="carousel-wrapper">
      {showArrows && isScrollable && (
        <>
          <button 
            type="button"
            onClick={handlePrev} 
            className="carousel-arrow left"
            aria-label="Anterior"
          >
            ‹
          </button>
          <button 
            type="button"
            onClick={handleNext} 
            className="carousel-arrow right"
            aria-label="Próximo"
          >
            ›
          </button>
        </>
      )}
      <div 
        ref={containerRef} 
        className={`carousel-container hide-scrollbar ${!isScrollable ? "center-content" : ""}`}
      >
        {children}
      </div>
    </div>
  );
}
