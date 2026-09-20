function validateForm() {
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value.trim();

  clearErrors();

  let isValid = true;

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email) {
    showError('email', 'Email không được để trống');
    isValid = false;
  } else if (!email.includes('@')) {
    showError('email', 'Email phải có dấu @');
    isValid = false;
  } else if (!emailRegex.test(email)) {
    showError('email', 'Sau dấu @ phải có tên miền hợp lệ, ví dụ @gmail.com');
    isValid = false;
  }

  // Validate Password
  if (!password) {
    showError('password', 'Mật khẩu không được để trống');
    isValid = false;
  } else if (password.length < 6) {
    showError('password', 'Mật khẩu phải có ít nhất 6 ký tự');
    isValid = false;
  }

  return isValid;
}

function showError(fieldId, message) {
  const field = document.getElementById(fieldId);
  field.style.outline = '2px solid red';

  const slot = document.getElementById(fieldId + '-error');
  if (slot) {
    slot.textContent = message;
  }
}

function clearFieldError(fieldId) {
  const field = document.getElementById(fieldId);
  if (field) {
    field.style.outline = '';
  }
  const slot = document.getElementById(fieldId + '-error');
  if (slot) {
    slot.textContent = '';
  }
}

function clearErrors() {
  document.querySelectorAll('.error-slot').forEach(el => el.textContent = '');
  document.querySelectorAll('.input, #email, #password').forEach(el => el.style.outline = '');
}

const emailField = document.getElementById('email');
if (emailField) {
  emailField.addEventListener('input', function () {
    clearFieldError('email');
  });
}

const passwordField = document.getElementById('password');
if (passwordField) {
  passwordField.addEventListener('input', function () {
    clearFieldError('password');
  });
}

const EYE_OPEN_ICON = `
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
    <circle cx="12" cy="12" r="3"></circle>
  </svg>
`;

const EYE_CLOSED_ICON = `
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20c-7 0-11-8-11-8a18.5 18.5 0 0 1 5.06-5.94"></path>
    <path d="M9.9 4.24A10.94 10.94 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"></path>
    <path d="M14.12 14.12A3 3 0 1 1 9.88 9.88"></path>
    <line x1="1" y1="1" x2="23" y2="23"></line>
  </svg>
`;

function togglePassword() {
  const passwordInput = document.getElementById('password');
  const toggleIcon = document.getElementById('togglePassword');
  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    toggleIcon.innerHTML = EYE_CLOSED_ICON;
  } else {
    passwordInput.type = 'password';
    toggleIcon.innerHTML = EYE_OPEN_ICON;
  }
}

const togglePasswordIcon = document.getElementById('togglePassword');
if (togglePasswordIcon) {
  togglePasswordIcon.addEventListener('click', togglePassword);
}

const loginForm = document.getElementById('loginForm');

if (loginForm) {
  loginForm.addEventListener('submit', async function (event) {
    event.preventDefault();

    if (!validateForm()) {
      return;
    }

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();

    const loginBtn = document.getElementById('loginBtn');

    loginBtn.disabled = true;
    loginBtn.textContent = 'Đang xử lý...';

    try {
      const response = await fetch('http://127.0.0.1:5000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          email: email,
          password: password
        })
      });

      const result = await response.json();

      if (!response.ok) {
        alert(result.error?.message || 'Đăng nhập thất bại');
        return;
      }

      console.log('Login success:', result);

      window.location.href = 'index.html';

    } catch (error) {
      console.error('Login error:', error);
      alert('Không thể kết nối tới Backend');
    } finally {
      loginBtn.disabled = false;
      loginBtn.textContent = 'Đăng Nhập';
    }
  });
}
