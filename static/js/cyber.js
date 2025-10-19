// Cyberpunk 2050 JavaScript Animations
document.addEventListener('DOMContentLoaded', function() {
    // Scroll-based background animation
    const body = document.body;
    let scrollPosition = 0;

    function updateBackground() {
        const newPosition = window.pageYOffset;
        const delta = newPosition - scrollPosition;
        scrollPosition = newPosition;

        // Dynamic background shift based on scroll
        const hue = (scrollPosition * 0.1) % 360;
        body.style.setProperty('--scroll-hue', hue + 'deg');
    }

    // Throttled scroll handler
    let ticking = false;
    window.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(function() {
                updateBackground();
                ticking = false;
            });
            ticking = true;
        }
    });

    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('scroll-animate');
            }
        });
    }, observerOptions);

    // Observe all cyber-cards
    document.querySelectorAll('.cyber-card').forEach(card => {
        observer.observe(card);
    });

    // Mouse tracking for dynamic effects
    document.addEventListener('mousemove', function(e) {
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;

        // Update CSS custom properties for mouse position
        document.documentElement.style.setProperty('--mouse-x', x);
        document.documentElement.style.setProperty('--mouse-y', y);
    });

    // Glitch effect on hover for important elements
    document.querySelectorAll('.glitch').forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.animationDuration = '0.1s';
        });

        element.addEventListener('mouseleave', function() {
            this.style.animationDuration = '2s';
        });
    });

    // Cyber button effects
    document.querySelectorAll('.cyber-btn').forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.classList.add('cyber-js');
        });

        button.addEventListener('mouseleave', function() {
            this.classList.remove('cyber-js');
        });
    });

    // Typing effect for cyber text
    function typeWriter(element, text, speed = 50) {
        let i = 0;
        element.textContent = '';

        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }

        type();
    }

    // Apply typing effect to cyber text elements
    document.querySelectorAll('.cyber-text').forEach(element => {
        const originalText = element.textContent;
        element.setAttribute('data-original', originalText);
        typeWriter(element, originalText);
    });

    // Neural network pulse effect
    function createNeuralPulse() {
        const dots = document.querySelectorAll('.neural-dot');
        dots.forEach((dot, index) => {
            setTimeout(() => {
                dot.style.animation = 'neuralPulse 1s ease-in-out';
            }, index * 200);
        });
    }

    // Trigger neural pulse every 5 seconds
    if (document.querySelector('.neural-dots')) {
        setInterval(createNeuralPulse, 5000);
        createNeuralPulse(); // Initial trigger
    }

    // Performance optimization: Reduce animations on low-performance devices
    if ('performance' in window && 'memory' in window.performance) {
        const memInfo = window.performance.memory;
        if (memInfo.usedJSHeapSize > memInfo.totalJSHeapSize * 0.8) {
            // Reduce animation complexity
            document.documentElement.style.setProperty('--animation-duration', '0.5s');
        }
    }

    // Cyberpunk sound effects (visual feedback)
    function createCyberSound() {
        // Create visual "sound" effect
        const soundWave = document.createElement('div');
        soundWave.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            width: 20px;
            height: 20px;
            border: 2px solid #00ffff;
            border-radius: 50%;
            animation: soundWave 1s ease-out forwards;
            pointer-events: none;
            z-index: 9999;
        `;

        soundWave.innerHTML = `
            <style>
                @keyframes soundWave {
                    0% { transform: scale(0); opacity: 1; }
                    100% { transform: scale(20); opacity: 0; }
                }
            </style>
        `;

        document.body.appendChild(soundWave);
        setTimeout(() => document.body.removeChild(soundWave), 1000);
    }

    // Add sound effect to buttons
    document.querySelectorAll('.cyber-btn').forEach(button => {
        button.addEventListener('click', createCyberSound);
    });

    console.log('🦾 Cyberpunk Neural Network Initialized - Welcome to 2050');
});