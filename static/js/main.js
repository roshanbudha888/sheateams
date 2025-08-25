  // Initialize rain effect
  document.addEventListener('DOMContentLoaded', function() {
      // Rain effect configuration
      particlesJS('rainContainer', {
          "particles": {
              "number": {
                  "value": 150,
                  "density": {
                      "enable": true,
                      "value_area": 800
                  }
              },
              "color": {
                  "value": "#ffffff"
              },
              "shape": {
                  "type": "circle",
                  "stroke": {
                      "width": 0,
                      "color": "#000000"
                  },
                  "polygon": {
                      "nb_sides": 5
                  }
              },
              "opacity": {
                  "value": 0.5,
                  "random": true,
                  "anim": {
                      "enable": false,
                      "speed": 1,
                      "opacity_min": 0.1,
                      "sync": false
                  }
              },
              "size": {
                  "value": 2,
                  "random": true,
                  "anim": {
                      "enable": false,
                      "speed": 40,
                      "size_min": 0.1,
                      "sync": false
                  }
              },
              "line_linked": {
                  "enable": false
              },
              "move": {
                  "enable": true,
                  "speed": 5,
                  "direction": "bottom",
                  "random": false,
                  "straight": false,
                  "out_mode": "out",
                  "bounce": false,
                  "attract": {
                      "enable": false,
                      "rotateX": 600,
                      "rotateY": 1200
                  }
              }
          },
          "interactivity": {
              "detect_on": "canvas",
              "events": {
                  "onhover": {
                      "enable": false
                  },
                  "onclick": {
                      "enable": false
                  },
                  "resize": true
              }
          },
          "retina_detect": true
      });
$(document).ready(function () {
    const $mobileMenu = $('.mobile-menu');
    const breakpoint = 992; // Same as CSS media query breakpoint

  // Mobile menu toggle
  $(".mobile-menu-btn").click(function (event) {
    event.preventDefault();
    event.stopPropagation();
    $(".mobile-menu").toggleClass('active');
  });

  $(window).resize(function(){
    //if window width is larger than breakpoint
    if ($(window).width() > breakpoint){
        //Ensure the mobile menu is hidden
        if ($mobileMenu.hasClass('active')){
            $mobileMenu.removeClass('active');
        }
    }
  });
});
  });