
/* =========================
   1. SLIDER ẢNH NỀN
   ========================= */

const slides = document.querySelectorAll('.slide');
const navBars = document.querySelectorAll('.nav-bar');
const appContainer = document.querySelector('.app-container');

let currentSlide = 0;
let slideInterval = null;

function showSlide(index) {
    if (slides.length === 0) return;

    index = (index + slides.length) % slides.length;

    slides.forEach(slide => slide.classList.remove('active'));
    navBars.forEach(bar => bar.classList.remove('active'));

    slides[index].classList.add('active');

    if (navBars[index]) {
        navBars[index].classList.add('active');
    }

    currentSlide = index;

    const currentTheme = slides[index].getAttribute('data-theme');

    if (appContainer && currentTheme) {
        appContainer.setAttribute('data-theme', currentTheme);
    }
}

function nextSlide() {
    showSlide(currentSlide + 1);
}

function stopSlide() {
    if (slideInterval !== null) {
        clearInterval(slideInterval);
        slideInterval = null;
    }
}

function startSlide() {
    stopSlide();

    if (slides.length > 1) {
        slideInterval = setInterval(nextSlide, 7000);
    }
}

function goToSlide(index) {
    showSlide(index);
    startSlide();
}

if (appContainer) {
    appContainer.addEventListener('mouseenter', stopSlide);
    appContainer.addEventListener('mouseleave', startSlide);
}

showSlide(0);
startSlide();


/* =========================
   2. LẤY CÁC THÀNH PHẦN LOGIN
   ========================= */

const loginForm = document.getElementById('loginForm');

const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');

const togglePasswordButton =
    document.getElementById('togglePassword');

const eyeIcon = document.getElementById('eyeIcon');

const usernameError = document.getElementById('usernameError');
const passwordError = document.getElementById('passwordError');

const loginMessage = document.getElementById('loginMessage');

const loginButton = document.getElementById('loginButton');
const buttonText = document.getElementById('buttonText');
const loadingSpinner = document.getElementById('loadingSpinner');

const forgotPasswordLink =
    document.getElementById('forgotPassword');


/* =========================
   3. HIỂN THỊ THÔNG BÁO LỖI
   ========================= */

function showFieldError(input, errorElement, message) {
    if (errorElement) {
        errorElement.textContent = message;
    }

    if (input) {
        input.classList.toggle('input-error', message !== '');

        input.setAttribute(
            'aria-invalid',
            message ? 'true' : 'false'
        );
    }
}

function clearLoginMessage() {
    if (loginMessage) {
        loginMessage.textContent = '';
        loginMessage.className = 'login-message';
    }
}

function showLoginMessage(message, type = 'error') {
    if (!loginMessage) return;

    loginMessage.textContent = message;
    loginMessage.className = 'login-message ' + type;
}


/* =========================
   4. KIỂM TRA USERNAME / EMAIL
   ========================= */

function isValidEmail(email) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(email);
}

function validateUsername() {
    if (!usernameInput) return false;

    const username = usernameInput.value;

    if (username.trim() === '') {
        showFieldError(
            usernameInput,
            usernameError,
            'Vui lòng nhập tài khoản.'
        );

        return false;
    }

    if (
        username.includes('@') &&
        !isValidEmail(username.trim())
    ) {
        showFieldError(
            usernameInput,
            usernameError,
            'Email không đúng định dạng.'
        );

        return false;
    }

    showFieldError(usernameInput, usernameError, '');
    return true;
}


/* =========================
   5. KIỂM TRA MẬT KHẨU
   ========================= */

function validatePassword() {
    if (!passwordInput) return false;

    // Không trim hoặc thay đổi mật khẩu người dùng nhập.
    if (passwordInput.value.length === 0) {
        showFieldError(
            passwordInput,
            passwordError,
            'Vui lòng nhập mật khẩu.'
        );

        return false;
    }

    showFieldError(passwordInput, passwordError, '');
    return true;
}


/* =========================
   6. HIỆN / ẨN MẬT KHẨU
   ========================= */

// eyeIcon trong HTML phải là một thẻ SVG duy nhất.

function setPasswordIcon(isVisible) {
    if (!eyeIcon) return;

    // Chỉ thay nội dung bên trong SVG hiện có, không tạo SVG lồng nhau.
    eyeIcon.replaceChildren();

    const ns = 'http://www.w3.org/2000/svg';

    if (isVisible) {
        // Mắt mở
        const path = document.createElementNS(ns, 'path');
        path.setAttribute(
            'd',
            'M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z'
        );

        const circle = document.createElementNS(ns, 'circle');
        circle.setAttribute('cx', '12');
        circle.setAttribute('cy', '12');
        circle.setAttribute('r', '3');

        eyeIcon.append(path, circle);
    } else {
        // Mắt gạch chéo
        const paths = [
            'M3 3l18 18',
            'M10.6 10.6a2 2 0 0 0 2.8 2.8',
            'M9.9 5.2A10.8 10.8 0 0 1 12 5c5 0 8.5 4.5 9.5 7-.4 1-1.2 2.1-2.2 3',
            'M6.2 6.2C3.9 7.7 2.7 9.8 2.5 12c.5 1.2 3.8 7 9.5 7 1.2 0 2.3-.3 3.3-.8'
        ];

        paths.forEach(d => {
            const path = document.createElementNS(ns, 'path');
            path.setAttribute('d', d);
            eyeIcon.appendChild(path);
        });
    }
}

if (togglePasswordButton && passwordInput && eyeIcon) {
    // Trạng thái mặc định: che mật khẩu, mắt gạch chéo.
    passwordInput.type = 'password';
    setPasswordIcon(false);

    togglePasswordButton.addEventListener('click', function () {
        const isHidden = passwordInput.type === 'password';

        passwordInput.type = isHidden ? 'text' : 'password';
        setPasswordIcon(isHidden);

        togglePasswordButton.setAttribute(
            'aria-label',
            isHidden ? 'Ẩn mật khẩu' : 'Hiển thị mật khẩu'
        );

        togglePasswordButton.setAttribute(
            'aria-pressed',
            String(isHidden)
        );
    });
}


/* =========================
   7. XÓA LỖI KHI NHẬP LẠI
   ========================= */

if (usernameInput) {
    usernameInput.addEventListener('input', function () {
        if (usernameInput.value.trim() !== '') {
            showFieldError(usernameInput, usernameError, '');
        }

        clearLoginMessage();
    });

    usernameInput.addEventListener('blur', validateUsername);
}

if (passwordInput) {
    passwordInput.addEventListener('input', function () {
        if (passwordInput.value.length > 0) {
            showFieldError(passwordInput, passwordError, '');
        }

        clearLoginMessage();
    });
}


/* =========================
   8. XỬ LÝ ĐĂNG NHẬP
   ========================= */

const API_BASE_URL = 'http://127.0.0.1:5000';

const ROLE_HOME = {
    USER:       '../user/user-dashboard.html',
    TECHNICIAN: '../tech/technician-dashboard.html',
    TEAM_LEAD:  '../mane/management-dashboard.html',
    ADMIN:      '../admin/admin.html',
};

if (loginForm) {
    loginForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        clearLoginMessage();

        const usernameIsValid = validateUsername();
        const passwordIsValid = validatePassword();

        if (!usernameIsValid || !passwordIsValid) {
            showLoginMessage(
                'Vui lòng kiểm tra lại thông tin đăng nhập.',
                'error'
            );

            const firstInvalidInput =
                loginForm.querySelector('.input-error');

            if (firstInvalidInput) {
                firstInvalidInput.focus();
            }

            return;
        }

        // Chuẩn bị UI loading
        const email = usernameInput.value.trim();
        const password = passwordInput.value;

        if (loginButton) loginButton.disabled = true;
        if (buttonText) buttonText.hidden = true;
        if (loadingSpinner) loadingSpinner.hidden = false;

        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ email, password }),
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                showLoginMessage(
                    result.error?.message || 'Đăng nhập thất bại.',
                    'error'
                );
                return;
            }

            const role = result.data?.user?.role;
            const target = ROLE_HOME[role];

            if (!target) {
                showLoginMessage(
                    'Vai trò không hợp lệ: ' + role,
                    'error'
                );
                return;
            }

            showLoginMessage('Đăng nhập thành công! Đang chuyển trang...', 'success');

            setTimeout(() => {
                window.location.href = target;
            }, 400);

        } catch (error) {
            console.error('Login error:', error);
            showLoginMessage(
                'Không thể kết nối đến Backend. Kiểm tra server.',
                'error'
            );
        } finally {
            if (loginButton) loginButton.disabled = false;
            if (buttonText) buttonText.hidden = false;
            if (loadingSpinner) loadingSpinner.hidden = true;
        }
    });
}


/* =========================
   9. QUÊN MẬT KHẨU
   ========================= */

if (forgotPasswordLink) {
    forgotPasswordLink.addEventListener('click', function (event) {
        event.preventDefault();

        clearLoginMessage();

        showLoginMessage(
            'Chức năng khôi phục mật khẩu hiện chưa được kết nối.',
            'info'
        );
    });
}
