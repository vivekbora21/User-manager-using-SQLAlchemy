// Toast functionality
function showToast(message, type) {
    const container = document.querySelector('.toast-container');
    if (!container) {
        // If no container, create one
        const newContainer = document.createElement('div');
        newContainer.className = 'toast-container';
        document.body.appendChild(newContainer);
        container = newContainer;
    }
    const toast = document.createElement('div');
    toast.className = `toast alert-${type} fade-slide`;
    toast.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i> ${message}`;
    container.appendChild(toast);
    // Remove after animation
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// On page load, check for query params
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const msg = urlParams.get('msg');
    if (msg) {
        showToast(msg, 'success');
    }
    const error = urlParams.get('error');
    if (error) {
        showToast(error, 'error');
    }
    // Remove existing toasts after animation
    document.querySelectorAll('.toast').forEach(toast => {
        setTimeout(() => {
            toast.remove();
        }, 3000);
    });
});
