/* ============================================================
   NEU HelpDesk — Admin Account Management
   ============================================================ */

const API_BASE_URL = "http://127.0.0.1:5000";
const PAGE_SIZE = 10;

// DOM
const searchInput  = document.getElementById("searchInput");
const roleFilter   = document.getElementById("roleFilter");
const statusFilter = document.getElementById("statusFilter");

const accountTableBody = document.getElementById("accountTableBody");
const emptyState       = document.getElementById("emptyState");
const loadingState     = document.getElementById("loadingState");
const errorState       = document.getElementById("errorState");
const notification     = document.getElementById("notification");

const paginationContainer = document.getElementById("paginationContainer");
const pageInfo = document.getElementById("pageInfo");
const btnPrev  = document.getElementById("btnPrev");
const btnNext  = document.getElementById("btnNext");

const confirmModal   = document.getElementById("confirmModal");
const confirmName    = document.getElementById("confirmName");
const btnCancelLock  = document.getElementById("btnCancelLock");
const btnConfirmLock = document.getElementById("btnConfirmLock");
const btnLogout      = document.getElementById("btnLogout");

// State
let accounts          = [];
let currentPage       = 1;
let selectedAccount   = null;
let notificationTimer = null;
let currentUserId     = null;
let searchTimer       = null;
let searchAbortCtrl   = null;


/* ============================================================
   AUTH GUARD — chặn vào trang khi chưa login / không phải ADMIN
   ============================================================ */

async function checkAdminAuth() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            method: "GET",
            credentials: "include",
        });
        const result = await response.json().catch(() => ({}));

        if (!response.ok || !result.success) {
            window.location.href = "../login/login.html";
            return null;
        }

        const user = result.data?.user;
        if (!user || user.role !== "ADMIN") {
            alert("Bạn không có quyền truy cập trang này.");
            window.location.href = "../login/login.html";
            return null;
        }

        return user;
    } catch (err) {
        console.error("checkAdminAuth error:", err);
        window.location.href = "../login/login.html";
        return null;
    }
}


/* ============================================================
   HELPERS
   ============================================================ */

function getErrorMessage(result, fallback) {
    return result?.error?.message || fallback;
}

function showNotification(message, type = "success") {
    notification.textContent = message;
    notification.className = `notification notification-${type}`;
    notification.hidden = false;

    clearTimeout(notificationTimer);
    notificationTimer = setTimeout(() => {
        notification.hidden = true;
    }, 4000);
}

async function apiRequest(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        credentials: "include",
        headers: {
            ...(options.headers || {}),
            ...(options.body ? { "Content-Type": "application/json" } : {}),
        },
    });

    const result = await response.json().catch(() => ({}));

    if (!response.ok || result.success === false) {
        if (response.status === 401) {
            window.location.href = "../login/login.html";
            throw new Error("Phiên đăng nhập đã hết hạn.");
        }
        throw new Error(
            getErrorMessage(result, `Yêu cầu thất bại (${response.status})`)
        );
    }

    return result;
}

function buildQueryString() {
    const params = new URLSearchParams();

    const search   = searchInput.value.trim();
    const role     = roleFilter.value;
    const isLocked = statusFilter.value;

    if (search)          params.set("search", search);
    if (role)            params.set("role", role);
    if (isLocked !== "") params.set("is_locked", isLocked);

    const q = params.toString();
    return q ? `?${q}` : "";
}


/* ============================================================
   LOAD — có abort request cũ để tránh race khi search nhanh
   ============================================================ */

async function loadAccounts({ showError = true } = {}) {
    if (searchAbortCtrl) searchAbortCtrl.abort();
    searchAbortCtrl = new AbortController();

    loadingState.hidden = false;
    errorState.hidden = true;
    emptyState.hidden = true;

    const tableWrapper = document.querySelector(".card .table-wrapper");
    if (tableWrapper) tableWrapper.style.visibility = "hidden";

    try {
        const response = await fetch(
            `${API_BASE_URL}/admin/users${buildQueryString()}`,
            {
                method: "GET",
                credentials: "include",
                signal: searchAbortCtrl.signal,
            }
        );
        const result = await response.json().catch(() => ({}));

        if (!response.ok || result.success === false) {
            if (response.status === 401) {
                window.location.href = "../login/login.html";
                return;
            }
            throw new Error(
                getErrorMessage(result, `Yêu cầu thất bại (${response.status})`)
            );
        }

        accounts = Array.isArray(result.data) ? result.data : [];

        const totalPages = Math.max(1, Math.ceil(accounts.length / PAGE_SIZE));
        if (currentPage > totalPages) currentPage = totalPages;

        if (tableWrapper) tableWrapper.style.visibility = "visible";
        renderAccounts();
    } catch (err) {
        if (err.name === "AbortError") return;

        console.error("loadAccounts error:", err);

        accounts = [];
        accountTableBody.replaceChildren();
        paginationContainer.hidden = true;
        emptyState.hidden = true;

        errorState.textContent = err.message;
        errorState.hidden = false;

        if (showError) showNotification(err.message, "error");
    } finally {
        loadingState.hidden = true;
    }
}


/* ============================================================
   RENDER
   ============================================================ */

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
    const pageAccounts = accounts.slice(startIndex, startIndex + PAGE_SIZE);

    pageAccounts.forEach((account) => {
        const row = document.createElement("tr");
        if (account.is_locked) row.classList.add("row-locked");

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
        statusBadge.textContent = account.is_locked ? "Đã khóa" : "Hoạt động";
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

        // Không cho admin tự khóa mình
        if (account.id === currentUserId) {
            actionButton.disabled = true;
            actionButton.title = "Bạn không thể tự khóa tài khoản của mình";
        }

        actionCell.appendChild(actionButton);

        row.append(idCell, nameCell, emailCell, roleCell, statusCell, actionCell);
        accountTableBody.appendChild(row);
    });

    paginationContainer.hidden = totalPages <= 1;

    pageInfo.textContent =
        `Hiển thị ${startIndex + 1}-${Math.min(startIndex + PAGE_SIZE, accounts.length)} / ${accounts.length} tài khoản`;

    btnPrev.disabled = currentPage === 1;
    btnNext.disabled = currentPage === totalPages;
}


/* ============================================================
   MODAL + ACTIONS
   ============================================================ */

function closeConfirmModal() {
    confirmModal.hidden = true;
    selectedAccount = null;
}

async function handleConfirmLock() {
    if (!selectedAccount) return;

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
    } catch (err) {
        showNotification(err.message, "error");
    } finally {
        btnConfirmLock.disabled = false;
    }
}

async function unlockAccount(account) {
    try {
        await apiRequest(
            `/admin/users/${encodeURIComponent(account.id)}/unlock`,
            { method: "PATCH" }
        );
        showNotification(`Đã mở khóa tài khoản ${account.name}.`);
        await loadAccounts({ showError: false });
    } catch (err) {
        showNotification(err.message, "error");
    }
}


/* ============================================================
   INIT
   ============================================================ */

(async function init() {
    const admin = await checkAdminAuth();
    if (!admin) return;

    currentUserId = admin.id;

    // Search (debounce)
    searchInput.addEventListener("input", () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => {
            currentPage = 1;
            loadAccounts();
        }, 300);
    });

    // Filters
    roleFilter.addEventListener("change", () => {
        currentPage = 1;
        loadAccounts();
    });

    statusFilter.addEventListener("change", () => {
        currentPage = 1;
        loadAccounts();
    });

    // Pagination
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

    // Row actions
    accountTableBody.addEventListener("click", (event) => {
        const button = event.target.closest("button[data-action]");
        if (!button || button.disabled) return;

        const account = accounts.find((item) => item.id === button.dataset.id);
        if (!account) return;

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

    // Modal actions
    btnCancelLock.addEventListener("click", closeConfirmModal);
    btnConfirmLock.addEventListener("click", handleConfirmLock);

    // Logout
    btnLogout.addEventListener("click", async () => {
        btnLogout.disabled = true;
        try {
            await apiRequest("/auth/logout", { method: "POST" });
        } catch (err) {
            console.error("Logout error:", err);
        } finally {
            window.location.href = "../login/login.html";
        }
    });

    // Escape closes modal
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !confirmModal.hidden) {
            closeConfirmModal();
        }
    });

    // Initial load
    await loadAccounts();
})();