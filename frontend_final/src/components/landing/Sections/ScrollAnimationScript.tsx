
import React from "react";

export const ScrollAnimationScript = () => {
  return (
    <script dangerouslySetInnerHTML={{
      __html: `
        document.addEventListener('DOMContentLoaded', function() {
          // Initialize citation bloom animation
          setTimeout(() => {
            document.querySelector('.citation-bloom')?.classList.add('active');
          }, 500);
          
          // Initialize scroll animations with staggered effect
          const scrollElements = document.querySelectorAll('.scroll-fade-in');
          
          // Create an Intersection Observer
          const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
              if (entry.isIntersecting) {
                // Add visible class with a small delay for staggered effect
                const delay = entry.target.dataset.delay || 0;
                setTimeout(() => {
                  entry.target.classList.add('visible');
                }, delay);
              } else {
                // Optional: remove the class when scrolled out of view
                // entry.target.classList.remove('visible');
              }
            });
          }, {
            root: null,
            threshold: 0.1,
            rootMargin: '-50px 0px'
          });
          
          // Observe all scroll animation elements
          scrollElements.forEach((el, index) => {
            // Add staggered delay based on child index within parent
            const staggerDelay = 100;
            el.dataset.delay = (index % 3) * staggerDelay;
            observer.observe(el);
          });
          
          // Add smooth transition between sections
          const sections = document.querySelectorAll('section');
          sections.forEach((section) => {
            observer.observe(section);
            section.classList.add('section-transition');
          });
        });
      `
    }} />
  );
};
