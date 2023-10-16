const openButtons = document.querySelectorAll('[data-open-modal]');
const closeButtons = document.querySelectorAll('[data-modal-close]');
const modal = document.querySelector('[data-modal]');

openButtons.forEach((openButton) => {
    openButton.addEventListener("click", () => {
        modal.showModal();
    });
});

closeButtons.forEach((closeButton) => {
    closeButton.addEventListener("click", () => {
        modal.close();
    });
});

modal.addEventListener("click", (e) => {
    const dialogDimensions = modal.getBoundingClientRect();
    if (
        e.clientX < dialogDimensions.left ||
        e.clientX > dialogDimensions.right ||
        e.clientY < dialogDimensions.top ||
        e.clientY > dialogDimensions.bottom
    ) {
        modal.close();
    }
});
