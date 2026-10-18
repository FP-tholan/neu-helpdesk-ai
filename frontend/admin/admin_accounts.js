const API_BASE_URL = "http://127.0.0.1:5000";
const PAGE_SIZE = 10;

// Các phần tử HTML
const searchInput = document.getElementById("searchInput");
const roleFilter = document.getElementById("roleFilter");
const statusFilter = document.getElementById("statusFilter");

const accountTableBody = document.getElementById("accountTableBody");
const emptyState = document.getElementById("emptyState");
const loadingState = document.getElementById("loadingState");
const errorState = document.getElementById("errorState");
const notification = document.getElementById("notification");

const paginationContainer = document.getElementById("paginationContainer");
const pageInfo = document.getElementById("pageInfo");
const btnPrev = document.getElementById("btnPrev");
const btnNext = document.getElementById("btnNext");

const confirmModal = document.getElementById("confirmModal");
const confirmName = document.getElementById("confirmName");
const btnCancelLock = document.getElementById("btnCancelLock");
const btnConfirmLock = document.getElementById("btnConfirmLock");
const btnLogout = document.getElementById("btnLogout");

// Dữ liệu và trạng thái giao diện
let accounts = [];
let currentPage = 1;
let selectedAccount = null;
let notificationTimer = null;

// Chuyển lỗi từ API thành thông báo dễ hiểu
function getErrorMessage(result, fallback) {
    return result?.error?.message || fallback;
}

// Hiển thị thông báo
function showNotification(message, type = "success") {
    notification.textContent = message;
    notification.className = `notification notification-${type}`;
    notification.hidden = false;

    clearTimeout(notificationTimer);

    notificationTimer = setTimeout(() => {
        notification.hidden = true;
    }, 4000);
}

// Gọi API và xử lý JSON
async function apiRequest(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        credentials: "include",
        headers: {
            ...(options.headers || {}),
            ...(options.body ? { "Content-Type": "application/json" } : {})
        }
    });

    const result = await response.json().catch(() => ({}));

    if (!response.ok || result.success === false) {
        throw new Error(
            getErrorMessage(result, `Yêu cầu thất bại (${response.status})`)
        );
    }

    return result;
}

// Tạo query string từ bộ tìm kiếm và lọc
function buildQueryString() {
    const params = new URLSearchParams();

    const search = searchInput.value.trim();
    const role = roleFilter.value;
    const isLocked = statusFilter.value;

    if (search) {
        params.set("search", search);
    }

    if (role) {
        params.set("role", role);
    }

    if (isLocked !== "") {
        params.set("is_locked", isLocked);
    }

    const query = params.toString();
    return query ? `?${query}` : "";
}

// Tải danh sách tài khoản
async function loadAccounts({ showError = true } = {}) {
    loadingState.hidden = false;
    errorState.hidden = true;
    emptyState.hidden = true;

    try {
        const result = await apiRequest(
            `/admin/users${buildQueryString()}`
        );

        accounts = Array.isArray(result.data) ? result.data : [];

        // Nếu lọc làm giảm số trang, đưa trang về phạm vi hợp lệ
        const totalPages = Math.max(1, Math.ceil(accounts.length / PAGE_SIZE));

        if (currentPage > totalPages) {
            currentPage = totalPages;
        }

        renderAccounts();
    } catch (error) {
        console.error("Không thể tải danh sách tài khoản:", error);

        accounts = [];
        accountTableBody.replaceChildren();
        paginationContainer.hidden = true;
        emptyState.hidden = true;

        errorState.textContent = error.message;
        errorState.hidden = false;

        if (showError) {
            showNotification(error.message, "error");
        }
    } finally {
        loadingState.hidden = true;
    }
}

// Hiển thị danh sách tài khoản
function renderAccounts() {
    accountTableBody.replaceChildren();

    if (accounts.length === 0) {
        emptyState.hidden = false;
        paginationContainer.hidden = true;
        return;
    }

    emptyState.hidden = true;

    const totalPages = Math.ceil(accounts.length / PAGE_SIZE);
    const startIndex = (currentPage - 1) * PAGE_SIZE;
    const pageAccounts = accounts.slice(
        startIndex,
        startIndex + PAGE_SIZE
    );

    pageAccounts.forEach((account) => {
        const row = document.createElement("tr");

        if (account.is_locked) {
            row.classList.add("row-locked");
        }

        // Các ô dữ liệu được tạo bằng textContent để tránh chèn HTML
        const idCell = document.createElement("td");
        idCell.textContent = account.id;

        const nameCell = document.createElement("td");
        nameCell.textContent = account.name;

        const emailCell = document.createElement("td");
        emailCell.textContent = account.email;

        const roleCell = document.createElement("td");
        const roleBadge = document.createElement("span");
        roleBadge.className = "role";
        roleBadge.textContent = account.role;
        roleCell.appendChild(roleBadge);

        const statusCell = document.createElement("td");
        const statusBadge = document.createElement("span");
        statusBadge.className = account.is_locked
            ? "status status-locked"
            : "status status-active";

        statusBadge.textContent = account.is_locked
            ? "Đã khóa"
            : "Hoạt động";

        statusCell.appendChild(statusBadge);

        const actionCell = document.createElement("td");
        actionCell.className = "col-action";

        const actionButton = document.createElement("button");
        actionButton.type = "button";
        actionButton.dataset.id = account.id;
        actionButton.dataset.action = account.is_locked ? "unlock" : "lock";

        if (account.is_locked) {
            actionButton.className = "btn-unlock";
            actionButton.textContent = "Mở khóa";
        } else {
            actionButton.className = "btn-lock";
            actionButton.textContent = "Khóa";
        }

        actionCell.appendChild(actionButton);

        row.append(
            idCell,
            nameCell,
            emailCell,
            roleCell,
            statusCell,
            actionCell
        );

        accountTableBody.appendChild(row);
    });

    paginationContainer.hidden = totalPages <= 1;

    pageInfo.textContent =
        `Hiển thị ${startIndex + 1}-${Math.min(startIndex + PAGE_SIZE, accounts.length)} / ${accounts.length} tài khoản`;

    btnPrev.disabled = currentPage === 1;
    btnNext.disabled = currentPage === totalPages;
}

// Tìm kiếm có độ trễ để tránh gọi API liên tục khi gõ
let searchTimer = null;

searchInput.addEventListener("input", () => {
    clearTimeout(searchTimer);

    searchTimer = setTimeout(() => {
        currentPage = 1;
        loadAccounts();
    }, 300);
});

// Khi thay đổi bộ lọc
roleFilter.addEventListener("change", () => {
    currentPage = 1;
    loadAccounts();
});

statusFilter.addEventListener("change", () => {
    currentPage = 1;
    loadAccounts();
});

// Chuyển trang
btnPrev.addEventListener("click", () => {
    if (currentPage > 1) {
        currentPage--;
        renderAccounts();
    }
});

btnNext.addEventListener("click", () => {
    const totalPages = Math.ceil(accounts.length / PAGE_SIZE);

    if (currentPage < totalPages) {
        currentPage++;
        renderAccounts();
    }
});

// Xử lý nhấn Khóa hoặc Mở khóa
accountTableBody.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-action]");

    if (!button) {
        return;
    }

    const account = accounts.find(
        (item) => item.id === button.dataset.id
    );

    if (!account) {
        return;
    }

    if (button.dataset.action === "lock") {
        selectedAccount = account;
        confirmName.textContent = account.name;
        confirmModal.hidden = false;
        btnConfirmLock.focus();
        return;
    }

    if (button.dataset.action === "unlock") {
        unlockAccount(account);
    }
});

// Đóng hộp thoại xác nhận khóa
function closeConfirmModal() {
    confirmModal.hidden = true;
    selectedAccount = null;
}

btnCancelLock.addEventListener("click", closeConfirmModal);

// Xác nhận khóa tài khoản
btnConfirmLock.addEventListener("click", async () => {
    if (!selectedAccount) {
        return;
    }

    const account = selectedAccount;
    btnConfirmLock.disabled = true;

    try {
        await apiRequest(
            `/admin/users/${encodeURIComponent(account.id)}/lock`,
            { method: "PATCH" }
        );

        closeConfirmModal();
        showNotification(`Đã khóa tài khoản ${account.name}.`);

        await loadAccounts({ showError: false });
    } catch (error) {
        showNotification(error.message, "error");
    } finally {
        btnConfirmLock.disabled = false;
    }
});

// Mở khóa tài khoản
async function unlockAccount(account) {
    try {
        await apiRequest(
            `/admin/users/${encodeURIComponent(account.id)}/unlock`,
            { method: "PATCH" }
        );

        showNotification(`Đã mở khóa tài khoản ${account.name}.`);

        await loadAccounts({ showError: false });
    } catch (error) {
        showNotification(error.message, "error");
    }
}

// Đăng xuất
btnLogout.addEventListener("click", async () => {
    btnLogout.disabled = true;

    try {
        await apiRequest("/auth/logout", {
            method: "POST"
        });

        window.location.href = "../login/login.html";
    } catch (error) {
        showNotification(error.message, "error");
    } finally {
        btnLogout.disabled = false;
    }
});

// Đóng modal khi nhấn Escape
document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !confirmModal.hidden) {
        closeConfirmModal();
    }
});

// Tải dữ liệu khi mở trang
loadAccounts();