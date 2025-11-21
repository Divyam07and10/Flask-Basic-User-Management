// Shared JS: toast renderer for Flask flash messages + password visibility toggles

document.addEventListener('DOMContentLoaded', function () {
  // ----- Toasts -----
  const toastContainer = document.getElementById('toast-container');
  if (toastContainer) {
    const toastElList = [].slice.call(toastContainer.querySelectorAll('.toast'));
    toastElList.forEach(function (toastEl) {
      const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
      toast.show();
    });
  }

  // ----- Password visibility toggles -----
  document.querySelectorAll('[data-password-toggle]').forEach(function (wrapper) {
    const input = wrapper.querySelector('input[type="password"], input[type="text"]');
    const toggleBtn = wrapper.querySelector('[data-toggle-eye]');
    if (!input || !toggleBtn) return;

    toggleBtn.addEventListener('click', function () {
      const isPassword = input.getAttribute('type') === 'password';
      input.setAttribute('type', isPassword ? 'text' : 'password');

      // swap icon classes if using Bootstrap icons or similar
      const showIcon = toggleBtn.querySelector('[data-eye-open]');
      const hideIcon = toggleBtn.querySelector('[data-eye-closed]');
      if (showIcon && hideIcon) {
        if (isPassword) {
          showIcon.classList.add('d-none');
          hideIcon.classList.remove('d-none');
        } else {
          showIcon.classList.remove('d-none');
          hideIcon.classList.add('d-none');
        }
      }
    });
  });
});
