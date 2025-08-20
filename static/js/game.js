// Create rain effect
function createRain() {
    const rainContainer = document.getElementById('rainContainer');
    const rainCount = 100;

    for (let i = 0; i < rainCount; i++) {
        const rainDrop = document.createElement('div');
        rainDrop.classList.add('rain-drop');

        // Random properties for each rain drop
        const left = Math.random() * 100;
        const animationDuration = 0.5 + Math.random() * 1.5;
        const animationDelay = Math.random() * 2;
        const height = 30 + Math.random() * 70;
        const opacity = 0.1 + Math.random() * 0.5;

        rainDrop.style.left = `${left}%`;
        rainDrop.style.animationDuration = `${animationDuration}s`;
        rainDrop.style.animationDelay = `${animationDelay}s`;
        rainDrop.style.height = `${height}px`;
        rainDrop.style.opacity = opacity;

        rainContainer.appendChild(rainDrop);
    }
}

// Modal functionality
function setupModal() {
    const modal = document.getElementById('gameModal');
    const closeModal = document.getElementById('closeModal');

    // Close modal when clicking X
    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    createRain();
    setupModal();

    // You can add more initialization code here
});