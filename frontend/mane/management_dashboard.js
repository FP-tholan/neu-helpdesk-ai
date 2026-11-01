// =============================================================
// Management Dashboard (TEAM_LEAD)
// =============================================================

const API_BASE_URL = 'http://127.0.0.1:5000';

let currentUser = null;
let currentSelectedTeam = null;
let pendingAssignTicketId = null;
let pendingAssignMode = 'assign';

let _cacheDashboard   = null;   // /management/dashboard
let _cacheUnassigned  = [];     // /management/tickets/unassigned
let _cacheTickets     = [];     // /management/tickets
let _cacheTechnicians = [];     // /management/technicians
let _cacheSettings    = { dispatch_mode: 1 };   // /management/settings

// =============================================================
// API HELPERS
// =============================================================

async function apiGet(path) {
  const r = await fetch(`${API_BASE_URL}${path}`, {
    method: 'GET',
    credentials: 'include',
  });
  const j = await r.json();
  return { status: r.status, body: j };
}

async function apiSend(method, path, payload) {
  const r = await fetch(`${API_BASE_URL}${path}`, {
    method,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: payload ? JSON.stringify(payload) : undefined,
  });
  const j = await r.json();
  return { status: r.status, body: j };
}


// =============================================================
// AUTH
// =============================================================

async function checkTeamLeadAuth() {
  try {
    const { status, body } = await apiGet('/auth/me');

    if (status === 401 || !body.success) {
      window.location.href = '../login/login.html';
      return null;
    }

    const user = body.data?.user;

    if (!user || user.role !== 'TEAM_LEAD') {
      alert('Bạn không có quyền truy cập trang này.');
      window.location.href = '../login/login.html';
      return null;
    }

    return user;
  } catch (e) {
    console.error('Check TEAM_LEAD auth error:', e);
    alert('Không thể kết nối đến Backend.');
    return null;
  }
}


async function logoutTeamLead() {
  try {
    await apiSend('POST', '/auth/logout');
  } catch (e) {
    console.error('Logout error:', e);
  }
  window.location.href = '../login/login.html';
}


// =============================================================
// INIT
// =============================================================

document.addEventListener('DOMContentLoaded', async () => {
  const user = await checkTeamLeadAuth();
  if (!user) return;

  currentUser = user;
  currentSelectedTeam = user.team_id;

  // Header
  const adminNameEl = document.getElementById('adminName');
  const adminMetaEl = document.getElementById('adminMeta');
  if (adminNameEl) adminNameEl.textContent = user.name;
  if (adminMetaEl) adminMetaEl.textContent = user.email || '';

  // Team badge
  const teamBadge = document.getElementById('currentTeamBadge');
  if (teamBadge) teamBadge.textContent = user.team_id || '—';

  // Logout
  const btnLogout = document.getElementById('btnLogout');
  if (btnLogout) btnLogout.addEventListener('click', logoutTeamLead);

  // Sidebar + tabs
  setupSidebarNavigation();

  document.querySelectorAll('.sub-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      switchView(btn.getAttribute('data-tab'));
    });
  });

  // Search
  const searchTechInput = document.getElementById('searchTechInput');
  if (searchTechInput) searchTechInput.addEventListener('input', renderTechsTable);

  // Assign modal
  const assignModal = document.getElementById('assignModal');
  document.getElementById('btnAssignModalClose')
    ?.addEventListener('click', () => assignModal.classList.remove('show'));
  document.getElementById('btnCancelAssign')
    ?.addEventListener('click', () => assignModal.classList.remove('show'));
  document.getElementById('btnConfirmAssign')
    ?.addEventListener('click', handleConfirmAssign);

  // Add member modal
  const addModal = document.getElementById('addMemberModal');
  document.getElementById('btnAddMember')
    ?.addEventListener('click', () => addModal.classList.add('show'));
  document.getElementById('btnAddMemberClose')
    ?.addEventListener('click', () => addModal.classList.remove('show'));
  document.getElementById('btnCancelAddMember')
    ?.addEventListener('click', () => addModal.classList.remove('show'));
  document.getElementById('addMemberForm')
    ?.addEventListener('submit', handleAddMember);

  // Settings — mode select
  document.getElementById('dispatchModeSelect')
    ?.addEventListener('change', (e) => {
      const hints = {
        '1': 'Ticket mới vào hàng đợi Team. Team Lead tự set priority, tự gán KTV. KTV resolve → chờ Team Lead nghiệm thu.',
        '2': 'Ticket mới được AI tự đặt priority. AI tắt → LOW. Hệ thống gán KTV workload thấp nhất. KTV resolve → tự đóng.',
      };
      const hint = document.getElementById('dispatchModeHint');
      if (hint) hint.textContent = hints[e.target.value] || '';
    });

  document.getElementById('btnSaveDispatchMode')
    ?.addEventListener('click', async () => {
      const mode = parseInt(document.getElementById('dispatchModeSelect').value, 10);
      const { status, body } = await apiSend('PUT', '/management/settings', {
        dispatch_mode: mode,
      });
      if (status !== 200 || !body.success) {
        alert(body.error || 'Không lưu được thiết lập.');
        return;
      }
      alert('Đã lưu chế độ phân công.');
      _cacheSettings.dispatch_mode = mode;
      await refreshAll();
    });

  // Auto-refresh mỗi 60s (dữ liệu cập nhật theo thời gian)
  setInterval(async () => {
    if (document.hidden) return;
    try { await refreshAll(); } catch (e) { /* ignore */ }
  }, 60000);

  // Initial load
  await refreshAll();
});


function renderSettings() {
  const sel  = document.getElementById('dispatchModeSelect');
  const hint = document.getElementById('dispatchModeHint');
  if (!sel) return;

  const mode = String(_cacheSettings.dispatch_mode || 1);
  sel.value = mode;

  const hints = {
    '1': 'Ticket mới vào hàng đợi Team. Team Lead tự set priority, tự gán KTV. KTV resolve → chờ Team Lead nghiệm thu.',
    '2': 'Ticket mới được AI tự đặt priority (LOW/MEDIUM/HIGH/CRITICAL). AI tắt → LOW. Hệ thống gán KTV workload thấp nhất. KTV resolve → tự đóng, không nghiệm thu.',
  };
  if (hint) hint.textContent = hints[mode] || '';
}


// =============================================================
// DATA
// =============================================================

async function refreshAll() {
  try {
    const [dash, unassigned, tickets, techs, settings] = await Promise.all([
      apiGet('/management/dashboard'),
      apiGet('/management/tickets/unassigned'),
      apiGet('/management/tickets'),
      apiGet('/management/technicians'),
      apiGet('/management/settings'),
    ]);

    if (dash.status === 401 || unassigned.status === 401) {
      window.location.href = '../login/login.html';
      return;
    }

    _cacheDashboard   = dash.body.data || null;
    _cacheUnassigned  = unassigned.body.data || [];
    _cacheTickets     = tickets.body.data || [];
    _cacheTechnicians = techs.body.data || [];
    _cacheSettings    = settings.body.data || { dispatch_mode: 1 };

    renderManagementDashboard();
    renderSettings();
  } catch (e) {
    console.error('refreshAll error:', e);
    alert('Không tải được dữ liệu. Kiểm tra Backend.');
  }
}


// =============================================================
// RENDER
// =============================================================

function renderManagementDashboard() {
  // ---- KPIs ----
  if (_cacheDashboard) {
    const s = _cacheDashboard.stats || {};
    const setText = (id, v) => {
      const el = document.getElementById(id);
      if (el) el.textContent = v;
    };
    setText('statTotalTechs',       s.total_techs ?? 0);
    setText('statActiveTechs',      s.active_techs ?? 0);
    setText('statUnassignedTickets', s.unassigned_tickets ?? 0);
    setText('statAvgRating',        '4.8 / 5');
  }

  renderTechsTable();
  renderDispatchView();
  renderTeamTicketsTable();
}


function renderTechsTable() {
  const tbody = document.getElementById('techsTableBody');
  if (!tbody) return;

  // Workload có trong /management/dashboard, không có trong /management/technicians
  // → ưu tiên dashboard, fallback technicians (để bảng vẫn có dữ liệu nếu dashboard lỗi)
  const source = (_cacheDashboard?.technicians?.length
    ? _cacheDashboard.technicians
    : _cacheTechnicians);

  const q = (document.getElementById('searchTechInput')?.value || '')
    .toLowerCase().trim();

  const filtered = source.filter(t => {
    if (!q) return true;
    return (
      (t.name  || '').toLowerCase().includes(q) ||
      (t.id    || '').toLowerCase().includes(q) ||
      (t.email || '').toLowerCase().includes(q)
    );
  });

  tbody.innerHTML = '';

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#94a3b8;">Không tìm thấy kỹ thuật viên phù hợp.</td></tr>`;
    return;
  }

  filtered.forEach(tech => {
    const tr = document.createElement('tr');
    const initials = (tech.name || 'KTV').trim().split(' ').pop().substring(0, 2).toUpperCase();

    // --- Workload (từ dashboard) ---
    const wl = tech.workload || { assigned: 0, in_progress: 0, total_open: 0 };
    const wlTotal   = wl.total_open   || 0;
    const wlAssigned = wl.assigned    || 0;
    const wlProgress = wl.in_progress || 0;

    // Màu + độ dài thanh theo tải
    const wlColor = wlTotal >= 4 ? '#dc2626' : (wlTotal >= 2 ? '#f59e0b' : '#10b981');
    const wlWidth = Math.min(wlTotal * 20, 100);   // 5 việc = full

    const workloadCellHtml = `
      <div class="workload-container">
        <div class="workload-text">
          <span><strong>${wlTotal}</strong> việc</span>
          <span>${wlAssigned} chờ · ${wlProgress} đang làm</span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill"
               style="width:${wlWidth}%;background:${wlColor};"></div>
        </div>
      </div>
    `;

    // --- Đánh giá: backend chưa có field rating, tạm hiển thị placeholder ---
    const ratingCellHtml = tech.rating != null
      ? `<span style="color:#f59e0b;font-weight:600;">★ ${Number(tech.rating).toFixed(1)}</span>
         <span style="font-size:11px;color:#94a3b8;">/5</span>`
      : `<span style="font-size:12px;color:#94a3b8;" title="Chưa có dữ liệu đánh giá">—</span>`;

    tr.innerHTML = `
      <td><strong>#${tech.id}</strong></td>
      <td>
        <div class="tech-cell">
          <div class="cell-avatar">${initials}</div>
          <div>
            <strong>${tech.name}</strong>
            <span style="display:block;font-size:11px;color:#64748b;">Kỹ thuật viên</span>
          </div>
        </div>
      </td>
      <td>${tech.email}</td>
      <td>
        <div style="display:flex;align-items:center;">
          <label class="toggle-switch">
            <input type="checkbox" ${tech.is_on_duty ? 'checked' : ''}
                   data-id="${tech.id}" class="status-toggle-input">
            <span class="slider"></span>
          </label>
          <span class="status-label-inline" style="color:${tech.is_on_duty ? '#10b981' : '#94a3b8'}">
            ${tech.is_on_duty ? 'Đang trực' : 'Tạm nghỉ'}
          </span>
        </div>
      </td>
      <td>${workloadCellHtml}</td>
      <td>${ratingCellHtml}</td>
      <td>
        <button class="btn btn-secondary"
                style="padding:4px 10px;font-size:11.5px;opacity:.6;cursor:not-allowed;"
                disabled
                title="Chức năng phân quyền chi tiết đang phát triển">
          Phân quyền
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  // Toggle sự kiện
  document.querySelectorAll('.status-toggle-input').forEach(input => {
    input.addEventListener('change', async (e) => {
      const techId = e.target.getAttribute('data-id');
      const target = e.target.checked;

      const { status, body } = await apiSend('PATCH', `/management/technicians/${techId}/duty`, {
        is_on_duty: target,
      });

      if (status !== 200 || !body.success) {
        alert(body.error || 'Không cập nhật được ca trực.');
        e.target.checked = !target;
        return;
      }

      await refreshAll();
    });
  });
}


function renderDispatchView() {
  // Unassigned count
  const countEl = document.getElementById('dispatchUnassignedCount');
  if (countEl) countEl.textContent = `${_cacheUnassigned.length} ticket`;

  // Unassigned list
  const unassignedList = document.getElementById('unassignedTicketsList');
  if (unassignedList) {
    unassignedList.innerHTML = '';

    if (_cacheUnassigned.length === 0) {
      unassignedList.innerHTML = `<div style="text-align:center;padding:30px;color:#94a3b8;font-size:13px;">Tất cả sự cố của Team đã được điều phối!</div>`;
    } else {
      _cacheUnassigned.forEach(ticket => {
        const buildingName = ticket.location?.building?.name || '—';
        const roomName     = ticket.location?.room?.name     || '—';
        const loc          = `${buildingName} - ${roomName}`;

        const div = document.createElement('div');
        div.className = 'unassigned-card';
        div.innerHTML = `
          <div class="unassigned-header">
            <strong>#${ticket.id}</strong>
            <span class="badge badge-warning">Ưu tiên: ${(ticket.priority || '').toUpperCase()}</span>
          </div>
          <h4 style="font-size:13.5px;color:#001f44;margin:4px 0;">${ticket.title}</h4>
          <p style="font-size:12px;color:#64748b;margin-bottom:8px;">📍 ${loc}</p>
          <button class="btn-assign-quick"
                  onclick="openAssignModal('${ticket.id}', 'assign')">
            Phân công ngay ➔
          </button>
        `;
        unassignedList.appendChild(div);
      });
    }
  }

  // Available techs
  const availableList = document.getElementById('availableTechsList');
  if (availableList) {
    availableList.innerHTML = '';
    const active = _cacheTechnicians.filter(t => t.is_on_duty);

    if (active.length === 0) {
      availableList.innerHTML = `<div style="text-align:center;padding:30px;color:#94a3b8;font-size:13px;">Chưa có KTV trong ca trực.</div>`;
    } else {
      active.forEach(tech => {
        const div = document.createElement('div');
        div.className = 'tech-dispatch-card';
        div.innerHTML = `
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
              <strong style="font-size:13.5px;color:#001f44;">${tech.name}</strong>
              <span style="display:block;font-size:11.5px;color:#64748b;">${tech.email}</span>
            </div>
            <span class="badge badge-success">Sẵn sàng nhận việc</span>
          </div>
        `;
        availableList.appendChild(div);
      });
    }
  }
}


function renderTeamTicketsTable() {
  const tbody = document.getElementById('teamTicketsTableBody');
  if (!tbody) return;

  tbody.innerHTML = '';
  if (_cacheTickets.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#94a3b8;">Không có ticket nào thuộc Team này.</td></tr>`;
    return;
  }

  _cacheTickets.forEach(ticket => {
    const loc = ticket.location
      ? `${ticket.location.building?.name || ''} - ${ticket.location.room?.name || ''}`
      : '—';

    const techName = ticket.assigned_to ? ticket.assigned_to.name : 'Chưa phân công';
    const status = (ticket.status || '').toLowerCase();
    const effPrio = ticket.effective_priority || ticket.priority;

    let actions = '';

    if (status === 'waiting_confirm') {
      actions = `
        <button class="btn btn-secondary"
                style="padding:4px 10px;font-size:11.5px;background:#dcfce7;color:#166534;border:1px solid #86efac;"
                onclick="verifyTicket('${ticket.id}')">✓ Nghiệm thu</button>
        <button class="btn btn-secondary"
                style="padding:4px 10px;font-size:11.5px;background:#fee2e2;color:#991b1b;border:1px solid #fca5a5;margin-left:4px;"
                onclick="rejectTicket('${ticket.id}')">✗ Từ chối</button>
      `;
    } else {
      actions = `
        <button class="btn btn-secondary"
                style="padding:4px 10px;font-size:11.5px;"
                onclick="openAssignModal('${ticket.id}', ${ticket.assigned_to ? "'reassign'" : "'assign'"})">
          ${ticket.assigned_to ? 'Đổi KTV' : 'Phân công'}
        </button>
      `;
    }

    const prioSelect = `
      <select class="priority-select" data-id="${ticket.id}"
              style="font-size:11.5px;padding:3px 6px;border-radius:4px;border:1px solid #cbd5e1;">
        ${['LOW','MEDIUM','HIGH','CRITICAL'].map(p =>
          `<option value="${p}" ${p === effPrio ? 'selected' : ''}>${p}</option>`
        ).join('')}
      </select>
    `;

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>#${ticket.id}</strong></td>
      <td>${ticket.title}</td>
      <td>${loc}</td>
      <td>${prioSelect}</td>
      <td><span class="badge badge-${status}">${ticket.status}</span></td>
      <td><strong>${techName}</strong></td>
      <td>${actions}</td>
    `;
    tbody.appendChild(tr);
  });

  tbody.querySelectorAll('.priority-select').forEach(sel => {
    sel.addEventListener('change', async (e) => {
      const ticketId = e.target.getAttribute('data-id');
      const newPrio = e.target.value;
      const { status, body } = await apiSend(
        'PATCH', `/management/tickets/${ticketId}/priority`,
        { priority: newPrio }
      );
      if (status !== 200 || !body.success) {
        alert(body.error || 'Không đổi được priority.');
        return;
      }
      await refreshAll();
    });
  });
}


// VERIFY / REJECT
window.verifyTicket = async function(ticketId) {
  if (!confirm(`Xác nhận nghiệm thu ticket #${ticketId}?`)) return;
  const { status, body } = await apiSend('POST', `/management/tickets/${ticketId}/verify`);
  if (status !== 200 || !body.success) {
    alert(body.error || 'Không nghiệm thu được.');
    return;
  }
  alert(`Đã nghiệm thu ticket #${ticketId}.`);
  await refreshAll();
};

window.rejectTicket = async function(ticketId) {
  const reason = prompt(`Lý do từ chối ticket #${ticketId} (bắt buộc):`);
  if (reason === null) return;
  if (!reason.trim()) { alert('Vui lòng nhập lý do.'); return; }
  const { status, body } = await apiSend(
    'POST', `/management/tickets/${ticketId}/reject`,
    { reason: reason.trim() }
  );
  if (status !== 200 || !body.success) {
    alert(body.error || 'Không từ chối được.');
    return;
  }
  alert(`Đã từ chối ticket #${ticketId}. Ticket quay lại hàng đợi KTV.`);
  await refreshAll();
};


// =============================================================
// ASSIGN MODAL
// =============================================================

window.openAssignModal = function(ticketId, mode) {
  pendingAssignTicketId = ticketId;
  pendingAssignMode = mode || 'assign';      

  // Tra title từ cache
  let ticketTitle = '';
  const fromUnassigned = _cacheUnassigned.find(t => t.id === ticketId);
  const fromAll = _cacheTickets.find(t => t.id === ticketId);
  if (fromUnassigned) ticketTitle = fromUnassigned.title;
  else if (fromAll) ticketTitle = fromAll.title;

  document.getElementById('assignModalTicketId').textContent = '#' + ticketId;
  document.getElementById('assignModalTicketTitle').textContent = ticketTitle || '';

  // Đổi title modal theo mode
  const modalTitle = document.querySelector('#assignModal .modal-header h2');
  if (modalTitle) {
    modalTitle.textContent = pendingAssignMode === 'reassign'
      ? 'Đổi kỹ thuật viên phụ trách'
      : 'Điều phối / Phân công sự cố';
  }

  const select = document.getElementById('assignTechSelect');
  select.innerHTML = '';

  const sourceForModal = (_cacheTechnicians?.length
    ? _cacheTechnicians
    : (_cacheDashboard?.technicians || []));
  let active = sourceForModal.filter(t => t.is_on_duty);

  // Nếu reassign, bỏ KTV hiện tại khỏi dropdown (tránh lỗi SAME_TECHNICIAN)
  if (pendingAssignMode === 'reassign') {
    const ticket = fromAll || fromUnassigned;
    const currentTechId = ticket?.assigned_to?.id;
    if (currentTechId) {
      active = active.filter(t => t.id !== currentTechId);
    }
  }

  if (active.length === 0) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = '— Không có KTV khả dụng —';
    select.appendChild(opt);
  } else {
    active.forEach(tech => {
      const opt = document.createElement('option');
      opt.value = tech.id;
      opt.textContent = `${tech.name} (${tech.email})`;
      select.appendChild(opt);
    });
  }

  document.getElementById('assignModal').classList.add('show');
};

async function handleConfirmAssign() {
  const techId = document.getElementById('assignTechSelect').value;
  if (!techId) {
    alert('Vui lòng chọn kỹ thuật viên.');
    return;
  }

  const endpoint = pendingAssignMode === 'reassign'
    ? `/management/tickets/${pendingAssignTicketId}/reassign`
    : `/management/tickets/${pendingAssignTicketId}/assign`;

  const { status, body } = await apiSend('POST', endpoint, {
    technician_id: techId,
  });

  if (status !== 200 || !body.success) {
    const errMap = {
      TICKET_ALREADY_ASSIGNED:       'Ticket đã được gán cho KTV khác. Thử "Đổi KTV".',
      TICKET_NOT_ASSIGNED:           'Ticket chưa được gán. Thử "Phân công".',
      SAME_TECHNICIAN:               'Đây đang là KTV phụ trách. Chọn KTV khác.',
      TICKET_NOT_ASSIGNABLE:         'Ticket không ở trạng thái có thể phân công.',
      TECHNICIAN_NOT_IN_TICKET_TEAM: 'KTV không thuộc team phụ trách ticket.',
      INVALID_TECHNICIAN:            'Người được chọn không phải kỹ thuật viên.',
      TICKET_NOT_FOUND:              'Không tìm thấy ticket.',
      TECHNICIAN_NOT_FOUND:          'Không tìm thấy kỹ thuật viên.',
    };
    alert(errMap[body.error] || body.error || 'Không phân công được.');
    return;
  }

  document.getElementById('assignModal').classList.remove('show');
  alert(pendingAssignMode === 'reassign'
    ? 'Đã đổi kỹ thuật viên phụ trách!'
    : 'Đã phân công thành công!');
  await refreshAll();
}


// =============================================================
// ADD MEMBER
// =============================================================

async function handleAddMember(e) {
  e.preventDefault();

  const username = document.getElementById('newTechUsername').value.trim();
  const name     = document.getElementById('newTechName').value.trim();
  const email    = document.getElementById('newTechEmail').value.trim();
  const password = document.getElementById('newTechPassword').value;

  if (!username || !name || !email || !password) {
    alert('Vui lòng điền đủ thông tin.');
    return;
  }
  if (password.length < 6) {
    alert('Mật khẩu tối thiểu 6 ký tự.');
    return;
  }

  const { status, body } = await apiSend('POST', '/management/technicians', {
    username, name, email, password,
  });

  if (status !== 201 || !body.success) {
    const errMap = {
      MISSING_FIELDS:  'Thiếu thông tin bắt buộc.',
      WEAK_PASSWORD:   'Mật khẩu quá ngắn.',
      EMAIL_EXISTS:    'Email đã tồn tại.',
      USERNAME_EXISTS: 'Username đã tồn tại.',
    };
    alert(errMap[body.error] || body.error || 'Không thêm được KTV.');
    return;
  }

  alert(`Đã thêm KTV ${body.data.name} vào Team.`);
  document.getElementById('addMemberModal').classList.remove('show');
  document.getElementById('addMemberForm').reset();
  await refreshAll();
}


// =============================================================
// VIEW SWITCH (giữ nguyên logic cũ)
// =============================================================

function switchView(viewKey) {
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

  const kpisSection = document.getElementById('mainKpisSection');
  const subTabsBar  = document.getElementById('subTabsBar');
  const titleEl     = document.getElementById('pageMainTitle');
  const descEl      = document.getElementById('pageMainDesc');

  kpisSection.style.display = 'grid';
  subTabsBar.style.display  = 'flex';

  if (viewKey === 'techs_list' || viewKey === 'navDashboard') {
    document.getElementById('tabContentTechs').classList.add('active');
    titleEl.textContent = 'Quản lý Đội ngũ & Điều phối';
    descEl.textContent  = 'Giám sát ca trực, hiệu suất KTV và điều phối sự cố CSVC & CNTT';
    syncSubTabActive('techs_list');
    syncSidebarActive('navDashboard');
  } else if (viewKey === 'dispatch_view' || viewKey === 'navDispatch') {
    document.getElementById('tabContentDispatch').classList.add('active');
    titleEl.textContent = 'Điều phối Công việc (Dispatch Hub)';
    descEl.textContent  = 'Phân công sự cố đang chờ xử lý cho các kỹ thuật viên trong ca trực';
    syncSubTabActive('dispatch_view');
    syncSidebarActive('navDispatch');
  } else if (viewKey === 'team_tickets' || viewKey === 'navTicketsList') {
    document.getElementById('tabContentTickets').classList.add('active');
    titleEl.textContent = 'Danh sách Sự cố của Đội';
    descEl.textContent  = 'Toàn bộ sự cố CSVC & CNTT thuộc quyền quản lý của Team';
    syncSubTabActive('team_tickets');
    syncSidebarActive('navTicketsList');
  } else if (viewKey === 'navReports') {
    document.getElementById('tabContentReports').classList.add('active');
    titleEl.textContent = 'Báo cáo Hiệu suất & SLA';
    descEl.textContent  = 'Chỉ số hoàn thành công việc và thời gian đáp ứng của Đội ngũ';
    subTabsBar.style.display = 'none';
    syncSidebarActive('navReports');
  } else if (viewKey === 'navSettings') {
    document.getElementById('tabContentSettings').classList.add('active');
    titleEl.textContent = 'Cài đặt Hệ thống Quản trị';
    descEl.textContent  = 'Cấu hình quy tắc điều phối tự động và hạn mức tải công việc';
    kpisSection.style.display = 'none';
    subTabsBar.style.display  = 'none';
    syncSidebarActive('navSettings');
  }
}


function syncSubTabActive(tabKey) {
  document.querySelectorAll('.sub-tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === tabKey);
  });
}

function syncSidebarActive(navId) {
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
    item.classList.toggle('active', item.id === navId);
  });
}

function setupSidebarNavigation() {
  const map = {
    navDashboard:    'navDashboard',
    navTicketsList:  'navTicketsList',
    navDispatch:     'navDispatch',
    navReports:      'navReports',
    navSettings:     'navSettings',
  };
  Object.keys(map).forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('click', (e) => {
      e.preventDefault();
      switchView(id);
    });
  });
}
