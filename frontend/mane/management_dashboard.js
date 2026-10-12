// Khởi tạo dữ liệu Đội ngũ & KTV cho Management Dashboard (Issue #20)
const SHARED_STORAGE_KEY = 'neu_helpdesk_shared_tickets';
const TEAMS_STORAGE_KEY = 'neu_helpdesk_teams_data';

const DEFAULT_SHARED_TICKETS = [
  {
    id: 'TCK-2026-001',
    reporter: 'Nguyễn Văn An (SV)',
    location: 'Nhà B - Phòng 102',
    building: 'Nhà B',
    title: 'Máy chiếu phòng B102 không lên tín hiệu',
    category: 'Thiết bị giảng dạy / Máy chiếu',
    priority: 'high',
    status: 'in_progress',
    assignedTeam: 'T_QTTB',
    assignedTech: 'Lê Hoàng Long',
    description: 'Bật nguồn máy chiếu có đèn nhưng màn chiếu không nhận cổng HDMI từ laptop giảng viên.',
    internalNotes: 'Đã kiểm tra nguồn, phát hiện cáp HDMI âm tường bị lỏng chân cắm.',
    history: [
      { time: '2026-09-28 08:30', title: 'Tạo ticket thành công', note: 'Người dùng gửi báo cáo sự cố qua hệ thống.', by: 'Nguyễn Văn An' },
      { time: '2026-09-28 08:45', title: 'Tiếp nhận xử lý', note: 'Phân công cho Team T_QTTB (KTV Lê Hoàng Long).', by: 'HelpDesk Dispatcher' }
    ]
  },
  {
    id: 'TCK-2026-002',
    reporter: 'Trần Thị Bình (GV)',
    location: 'Nhà A1 - Sảnh chính tầng 1',
    building: 'Nhà A1',
    title: 'Mạng Wi-Fi NEU-Student chập chờn tại sảnh A1',
    category: 'Mạng & Hạ tầng CNTT',
    priority: 'medium',
    status: 'assigned',
    assignedTeam: 'T_IT',
    assignedTech: 'Chưa phân công',
    description: 'Sinh viên không thể kết nối hoặc liên tục bị ngắt kết nối khi đang học trực tuyến.',
    internalNotes: '',
    history: [
      { time: '2026-09-29 10:15', title: 'Tạo ticket', note: 'Yêu cầu hỗ trợ hạ tầng mạng.', by: 'Trần Thị Bình' }
    ]
  },
  {
    id: 'TCK-2026-003',
    reporter: 'Ban Tổ Chức Hội Thảo',
    location: 'Hội trường A2',
    building: 'Hội trường A2',
    title: 'Micro không dây phòng hội trường A2 bị rè',
    category: 'Âm thanh & Ánh sáng',
    priority: 'critical',
    status: 'assigned',
    assignedTeam: 'T_PSA',
    assignedTech: 'Chưa phân công',
    description: 'Micro số 1 và số 2 bị nhiễu sóng và rè khi nói to.',
    internalNotes: '',
    history: [
      { time: '2026-09-30 08:00', title: 'Tạo ticket khẩn cấp', note: 'Cần xử lý trước giờ hội thảo chiều nay.', by: 'Ban Tổ Chức' }
    ]
  },
  {
    id: 'TCK-2026-004',
    reporter: 'Nguyễn Văn An (SV)',
    location: 'Nhà C - Phòng 301',
    building: 'Nhà C',
    title: 'Điều hòa phòng C301 không mát và rỉ nước',
    category: 'Điện lạnh & CSVC',
    priority: 'low',
    status: 'resolved',
    assignedTeam: 'T_QTTB',
    assignedTech: 'Lê Hoàng Long',
    description: 'Điều hòa nhiệt độ cài 18 độ nhưng phòng vẫn nóng, có nước nhỏ giọt xuống sàn.',
    internalNotes: 'Đã nạp bổ sung 2kg gas R410A và thông đường ống ngưng.',
    history: [
      { time: '2026-09-20 14:00', title: 'Tạo ticket', note: 'Báo lỗi điều hòa.', by: 'Nguyễn Văn An' },
      { time: '2026-09-20 16:30', title: 'Đã xử lý xong (Resolved)', note: 'Đã bảo dưỡng và nạp ga hoàn chỉnh.', by: 'Lê Hoàng Long' }
    ]
  }
];

const DEFAULT_TEAMS_DATA = {
  T_QTTB: {
    teamName: 'T_QTTB (Quản trị thiết bị)',
    avgRating: '4.8 / 5',
    techs: [
      { id: 'KV001', name: 'Lê Hoàng Long', email: 'longlh@neu.edu.vn', phone: '0981 112 233', role: 'Kỹ thuật viên chính', active: true, rating: '4.9', workload: 85, openTickets: 3 },
      { id: 'KV002', name: 'Trần Văn Hưng', email: 'hungtv@neu.edu.vn', phone: '0972 334 455', role: 'Kỹ thuật viên chính', active: true, rating: '4.7', workload: 40, openTickets: 1 },
      { id: 'KV003', name: 'Nguyễn Thành Nam', email: 'namnt@neu.edu.vn', phone: '0912 667 788', role: 'Hỗ trợ kỹ thuật', active: true, rating: '4.8', workload: 20, openTickets: 1 },
      { id: 'KV004', name: 'Đặng Quốc Huy', email: 'huydq@neu.edu.vn', phone: '0963 889 900', role: 'Hỗ trợ kỹ thuật', active: false, rating: '4.6', workload: 0, openTickets: 0 }
    ]
  },
  T_IT: {
    teamName: 'T_IT (Trung tâm CNTT / Mạng)',
    avgRating: '4.7 / 5',
    techs: [
      { id: 'KV010', name: 'Đỗ Tuấn Kiệt', email: 'kietdt@neu.edu.vn', phone: '0904 556 778', role: 'Kỹ thuật viên chính', active: true, rating: '4.8', workload: 70, openTickets: 2 },
      { id: 'KV011', name: 'Phạm Hồng Quân', email: 'quanph@neu.edu.vn', phone: '0936 123 789', role: 'Hỗ trợ kỹ thuật', active: true, rating: '4.6', workload: 30, openTickets: 1 },
      { id: 'KV012', name: 'Vũ Đức Thịnh', email: 'thinhvd@neu.edu.vn', phone: '0988 990 011', role: 'Hỗ trợ kỹ thuật', active: false, rating: '4.7', workload: 0, openTickets: 0 }
    ]
  },
  T_PSA: {
    teamName: 'T_PSA (Âm thanh & Ánh sáng)',
    avgRating: '4.9 / 5',
    techs: [
      { id: 'KV020', name: 'Bùi Đức Anh', email: 'anhbd@neu.edu.vn', phone: '0977 445 566', role: 'Kỹ thuật viên chính', active: true, rating: '5.0', workload: 50, openTickets: 1 },
      { id: 'KV021', name: 'Ngô Gia Huy', email: 'huyng@neu.edu.vn', phone: '0915 223 344', role: 'Hỗ trợ kỹ thuật', active: true, rating: '4.8', workload: 30, openTickets: 1 }
    ]
  }
};

function getTeamsData() {
  const data = localStorage.getItem(TEAMS_STORAGE_KEY);
  if (!data) {
    localStorage.setItem(TEAMS_STORAGE_KEY, JSON.stringify(DEFAULT_TEAMS_DATA));
    return DEFAULT_TEAMS_DATA;
  }
  try {
    return JSON.parse(data);
  } catch (e) {
    return DEFAULT_TEAMS_DATA;
  }
}

function saveTeamsData(data) {
  localStorage.setItem(TEAMS_STORAGE_KEY, JSON.stringify(data));
}

function getStoredTickets() {
  const data = localStorage.getItem(SHARED_STORAGE_KEY);
  if (!data) {
    localStorage.setItem(SHARED_STORAGE_KEY, JSON.stringify(DEFAULT_SHARED_TICKETS));
    return DEFAULT_SHARED_TICKETS;
  }
  try {
    const list = JSON.parse(data);
    if (!Array.isArray(list) || list.length === 0) {
      localStorage.setItem(SHARED_STORAGE_KEY, JSON.stringify(DEFAULT_SHARED_TICKETS));
      return DEFAULT_SHARED_TICKETS;
    }
    return list;
  } catch(e) {
    return DEFAULT_SHARED_TICKETS;
  }
}

function saveStoredTickets(tickets) {
  localStorage.setItem(SHARED_STORAGE_KEY, JSON.stringify(tickets));
}

const API_BASE_URL = 'http://127.0.0.1:5000';

let currentSelectedTeam = 'T_QTTB';
let pendingAssignTicketId = null;


async function checkTeamLeadAuth() {
  try {
    const response = await fetch(
      `${API_BASE_URL}/auth/me`,
      {
        method: 'GET',
        credentials: 'include'
      }
    );

    const result = await response.json();

    if (!response.ok) {
      window.location.href = '../login/login.html';
      return null;
    }

    const user = result.data?.user;

    if (!user || user.role !== 'TEAM_LEAD') {
      alert('Bạn không có quyền truy cập trang này.');
      window.location.href = '../login/login.html';
      return null;
    }

    return user;

  } catch (error) {
    console.error('Check TEAM_LEAD auth error:', error);
    alert('Không thể kết nối đến Backend.');
    return null;
  }
}


async function logoutTeamLead() {
  try {
    await fetch(
      `${API_BASE_URL}/auth/logout`,
      {
        method: 'POST',
        credentials: 'include'
      }
    );
  } catch (error) {
    console.error('Logout error:', error);
  }

  window.location.href = '../login/login.html';
}


function lockTeamToSession(user) {
  const teamSelector = document.getElementById('teamSelector');
  const teamBadge = document.getElementById('currentTeamBadge');

  if (user.team_id) {
    currentSelectedTeam = user.team_id;
  }

  if (teamSelector) {
    if (
      user.team_id &&
      !Array.from(teamSelector.options).some(
        option => option.value === user.team_id
      )
    ) {
      const option = document.createElement('option');
      option.value = user.team_id;
      option.textContent = user.team_id;
      teamSelector.appendChild(option);
    }

    teamSelector.value = currentSelectedTeam;
    teamSelector.disabled = true;
  }

  if (teamBadge) {
    teamBadge.textContent = currentSelectedTeam;
  }
}


document.addEventListener('DOMContentLoaded', async () => {
  const user = await checkTeamLeadAuth();

  if (!user) {
    return;
  }

  const adminNameEl = document.getElementById('adminName');
  const adminMetaEl = document.getElementById('adminMeta');

  if (adminNameEl) {
    adminNameEl.textContent = user.name;
  }

  if (adminMetaEl) {
    adminMetaEl.textContent = user.email || '';
  }

  lockTeamToSession(user);

  const btnLogout = document.getElementById('btnLogout');

  if (btnLogout) {
    btnLogout.addEventListener('click', logoutTeamLead);
  }

  // Gắn sự kiện chuyển trang cho toàn bộ Sidebar bên trái
  setupSidebarNavigation();

  // Sub Tab Switching bên trên bảng
  document.querySelectorAll('.sub-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const tabId = btn.getAttribute('data-tab');
      switchView(tabId);
    });
  });

  // Search Tech
  document.getElementById('searchTechInput').addEventListener('input', renderTechsTable);

  // Quick Assign Modal Events
  const assignModal = document.getElementById('assignModal');
  document.getElementById('btnAssignModalClose').addEventListener('click', () => assignModal.classList.remove('show'));
  document.getElementById('btnCancelAssign').addEventListener('click', () => assignModal.classList.remove('show'));
  document.getElementById('btnConfirmAssign').addEventListener('click', handleConfirmAssign);

  // Add Member Modal Events
  const addModal = document.getElementById('addMemberModal');
  document.getElementById('btnAddMember').addEventListener('click', () => addModal.classList.add('show'));
  document.getElementById('btnAddMemberClose').addEventListener('click', () => addModal.classList.remove('show'));
  document.getElementById('btnCancelAddMember').addEventListener('click', () => addModal.classList.remove('show'));
  document.getElementById('addMemberForm').addEventListener('submit', handleAddMember);

  // Render khởi tạo
  renderManagementDashboard();
});

// Điều khiển chuyển đổi màn hình linh hoạt
function switchView(viewKey) {
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

  const kpisSection = document.getElementById('mainKpisSection');
  const subTabsBar = document.getElementById('subTabsBar');
  const titleEl = document.getElementById('pageMainTitle');
  const descEl = document.getElementById('pageMainDesc');

  // Mặc định hiện KPIs và SubTabs
  kpisSection.style.display = 'grid';
  subTabsBar.style.display = 'flex';

  if (viewKey === 'techs_list' || viewKey === 'navDashboard') {
    document.getElementById('tabContentTechs').classList.add('active');
    titleEl.textContent = 'Quản lý Đội ngũ & Điều phối';
    descEl.textContent = 'Giám sát ca trực, hiệu suất KTV và điều phối sự cố CSVC & CNTT';
    syncSubTabActive('techs_list');
    syncSidebarActive('navDashboard');
  } 
  else if (viewKey === 'dispatch_view' || viewKey === 'navDispatch') {
    document.getElementById('tabContentDispatch').classList.add('active');
    titleEl.textContent = 'Điều phối Công việc (Dispatch Hub)';
    descEl.textContent = 'Phân công sự cố đang chờ xử lý cho các kỹ thuật viên trong ca trực';
    syncSubTabActive('dispatch_view');
    syncSidebarActive('navDispatch');
  } 
  else if (viewKey === 'team_tickets' || viewKey === 'navTicketsList') {
    document.getElementById('tabContentTickets').classList.add('active');
    titleEl.textContent = 'Danh sách Sự cố của Đội';
    descEl.textContent = 'Toàn bộ sự cố CSVC & CNTT thuộc quyền quản lý của Team';
    syncSubTabActive('team_tickets');
    syncSidebarActive('navTicketsList');
  } 
  else if (viewKey === 'navReports') {
    document.getElementById('tabContentReports').classList.add('active');
    titleEl.textContent = 'Báo cáo Hiệu suất & SLA';
    descEl.textContent = 'Chỉ số hoàn thành công việc và thời gian đáp ứng của Đội ngũ';
    subTabsBar.style.display = 'none'; // Ẩn sub tabs khi ở trang báo cáo
    syncSidebarActive('navReports');
  } 
  else if (viewKey === 'navSettings') {
    document.getElementById('tabContentSettings').classList.add('active');
    titleEl.textContent = 'Cài đặt Hệ thống Quản trị';
    descEl.textContent = 'Cấu hình quy tắc điều phối tự động và hạn mức tải công việc';
    kpisSection.style.display = 'none'; // Ẩn KPIs khi ở trang cài đặt
    subTabsBar.style.display = 'none';
    syncSidebarActive('navSettings');
  }
}

function syncSubTabActive(tabKey) {
  document.querySelectorAll('.sub-tab-btn').forEach(btn => {
    if (btn.getAttribute('data-tab') === tabKey) btn.classList.add('active');
    else btn.classList.remove('active');
  });
}

function syncSidebarActive(navId) {
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
    if (item.id === navId) item.classList.add('active');
    else item.classList.remove('active');
  });
}

function setupSidebarNavigation() {
  const navDashboard = document.getElementById('navDashboard');
  const navTicketsList = document.getElementById('navTicketsList');
  const navDispatch = document.getElementById('navDispatch');
  const navReports = document.getElementById('navReports');
  const navSettings = document.getElementById('navSettings');

  navDashboard.addEventListener('click', (e) => { e.preventDefault(); switchView('navDashboard'); });
  navTicketsList.addEventListener('click', (e) => { e.preventDefault(); switchView('navTicketsList'); });
  navDispatch.addEventListener('click', (e) => { e.preventDefault(); switchView('navDispatch'); });
  navReports.addEventListener('click', (e) => { e.preventDefault(); switchView('navReports'); });
  navSettings.addEventListener('click', (e) => { e.preventDefault(); switchView('navSettings'); });
}

function renderManagementDashboard() {
  const teams = getTeamsData();
  const team = teams[currentSelectedTeam] || teams['T_QTTB'];
  const tickets = getStoredTickets();

  // 1. Tính toán KPIs
  const totalTechs = team.techs.length;
  const activeTechs = team.techs.filter(t => t.active).length;
  const teamTickets = tickets.filter(t => t.assignedTeam === currentSelectedTeam);
  const unassignedCount = teamTickets.filter(t => t.status === 'assigned' || t.assignedTech === 'Chưa phân công' || t.assignedTech === 'Chờ phân công').length;

  document.getElementById('statTotalTechs').textContent = totalTechs;
  document.getElementById('statActiveTechs').textContent = activeTechs;
  document.getElementById('statUnassignedTickets').textContent = unassignedCount;
  document.getElementById('statAvgRating').textContent = team.avgRating || '4.8 / 5';

  renderTechsTable();
  renderDispatchView();
  renderTeamTicketsTable();
}

// Render Bảng Kỹ thuật viên (Tab 1)
function renderTechsTable() {
  const teams = getTeamsData();
  const team = teams[currentSelectedTeam];
  const query = document.getElementById('searchTechInput').value.toLowerCase().trim();

  const filtered = team.techs.filter(t => {
    return t.name.toLowerCase().includes(query) || t.id.toLowerCase().includes(query) || t.phone.includes(query) || t.email.toLowerCase().includes(query);
  });

  const tbody = document.getElementById('techsTableBody');
  tbody.innerHTML = '';

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#94a3b8;">Không tìm thấy kỹ thuật viên phù hợp.</td></tr>`;
    return;
  }

  filtered.forEach(tech => {
    const tr = document.createElement('tr');

    let barColor = '#10b981';
    if (tech.workload > 70) barColor = '#ef4444';
    else if (tech.workload > 40) barColor = '#f59e0b';

    const words = tech.name.trim().split(' ');
    const initials = words[words.length - 1].substring(0, 2).toUpperCase();

    tr.innerHTML = `
      <td><strong>#${tech.id}</strong></td>
      <td>
        <div class="tech-cell">
          <div class="cell-avatar">${initials}</div>
          <div>
            <strong>${tech.name}</strong>
            <span style="display:block;font-size:11px;color:#64748b;">${tech.role}</span>
          </div>
        </div>
      </td>
      <td>
        <div>${tech.email}</div>
        <span style="font-size:11px;color:#64748b;">${tech.phone}</span>
      </td>
      <td>
        <div style="display:flex;align-items:center;">
          <label class="toggle-switch">
            <input type="checkbox" ${tech.active ? 'checked' : ''} data-id="${tech.id}" class="status-toggle-input">
            <span class="slider"></span>
          </label>
          <span class="status-label-inline" style="color:${tech.active ? '#10b981' : '#94a3b8'}">
            ${tech.active ? 'Đang trực' : 'Tạm nghỉ'}
          </span>
        </div>
      </td>
      <td>
        <div class="workload-container">
          <div class="workload-text">
            <span>Tải: <strong>${tech.workload}%</strong></span>
            <span>(${tech.openTickets} việc)</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width:${tech.workload}%; background-color:${barColor};"></div>
          </div>
        </div>
      </td>
      <td><strong>⭐ ${tech.rating}</strong></td>
      <td>
        <button class="btn btn-secondary" style="padding:4px 10px;font-size:11.5px;" onclick="alert('Cấu hình phân quyền vai trò cho KTV ' + '${tech.name}');">Phân quyền</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  // Gắn sự kiện Toggle Trạng thái ca trực (status_toggle)
  document.querySelectorAll('.status-toggle-input').forEach(input => {
    input.addEventListener('change', (e) => {
      const techId = e.target.getAttribute('data-id');
      const targetTech = team.techs.find(t => t.id === techId);
      if (targetTech) {
        targetTech.active = e.target.checked;
        saveTeamsData(teams);
        renderManagementDashboard();
      }
    });
  });
}

// Render Điều phối công việc (Tab 2)
function renderDispatchView() {
  const tickets = getStoredTickets();
  const teamTickets = tickets.filter(t => t.assignedTeam === currentSelectedTeam);
  const unassigned = teamTickets.filter(t => t.status === 'assigned' || t.assignedTech === 'Chưa phân công' || t.assignedTech === 'Chờ phân công');

  document.getElementById('dispatchUnassignedCount').textContent = `${unassigned.length} ticket`;

  const unassignedList = document.getElementById('unassignedTicketsList');
  unassignedList.innerHTML = '';

  if (unassigned.length === 0) {
    unassignedList.innerHTML = `<div style="text-align:center;padding:30px;color:#94a3b8;font-size:13px;">Tất cả sự cố của Team đã được điều phối!</div>`;
  } else {
    unassigned.forEach(ticket => {
      const div = document.createElement('div');
      div.className = 'unassigned-card';
      div.innerHTML = `
        <div class="unassigned-header">
          <strong>#${ticket.id}</strong>
          <span class="badge badge-warning">Ưu tiên: ${ticket.priority.toUpperCase()}</span>
        </div>
        <h4 style="font-size:13.5px;color:#001f44;margin:4px 0;">${ticket.title}</h4>
        <p style="font-size:12px;color:#64748b;margin-bottom:8px;">📍 ${ticket.location} • Người báo: ${ticket.reporter}</p>
        <button class="btn-assign-quick" onclick="openAssignModal('${ticket.id}', '${ticket.title.replace(/'/g, "\'")}')">Phân công ngay ➔</button>
      `;
      unassignedList.appendChild(div);
    });
  }

  // Danh sách KTV đang sẵn sàng
  const teams = getTeamsData();
  const team = teams[currentSelectedTeam];
  const activeTechs = team.techs.filter(t => t.active);

  const availableList = document.getElementById('availableTechsList');
  availableList.innerHTML = '';

  activeTechs.forEach(tech => {
    const div = document.createElement('div');
    div.className = 'tech-dispatch-card';
    div.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <strong style="font-size:13.5px;color:#001f44;">${tech.name}</strong>
          <span style="display:block;font-size:11.5px;color:#64748b;">${tech.role} • ⭐ ${tech.rating}</span>
        </div>
        <span class="badge badge-success">Sẵn sàng nhận việc</span>
      </div>
      <div class="workload-text" style="margin-top:8px;">
        <span>Tải hiện tại: <strong>${tech.workload}%</strong></span>
        <span>${tech.openTickets} sự cố đang mở</span>
      </div>
      <div class="progress-bar-bg">
        <div class="progress-bar-fill" style="width:${tech.workload}%; background-color:${tech.workload > 70 ? '#ef4444' : '#10b981'};"></div>
      </div>
    `;
    availableList.appendChild(div);
  });
}

// Render Tất cả Ticket thuộc Team (Tab 3)
function renderTeamTicketsTable() {
  const tickets = getStoredTickets();
  const teamTickets = tickets.filter(t => t.assignedTeam === currentSelectedTeam);
  const tbody = document.getElementById('teamTicketsTableBody');
  tbody.innerHTML = '';

  if (teamTickets.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#94a3b8;">Không có ticket nào thuộc Team này.</td></tr>`;
    return;
  }

  teamTickets.forEach(ticket => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>#${ticket.id}</strong></td>
      <td>${ticket.title}</td>
      <td>${ticket.location}</td>
      <td><span class="badge" style="background:#f1f5f9;color:#334155;">${ticket.priority.toUpperCase()}</span></td>
      <td><span class="badge badge-${ticket.status}">${ticket.status}</span></td>
      <td><strong>${ticket.assignedTech}</strong></td>
      <td>
        <button class="btn btn-secondary" style="padding:4px 10px;font-size:11.5px;" onclick="openAssignModal('${ticket.id}', '${ticket.title.replace(/'/g, "\'")}')">Điều phối lại</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// Mở Modal Phân công nhanh
window.openAssignModal = function(ticketId, ticketTitle) {
  pendingAssignTicketId = ticketId;
  document.getElementById('assignModalTicketId').textContent = '#' + ticketId;
  document.getElementById('assignModalTicketTitle').textContent = ticketTitle;

  const teams = getTeamsData();
  const team = teams[currentSelectedTeam];
  const select = document.getElementById('assignTechSelect');
  select.innerHTML = '';

  team.techs.filter(t => t.active).forEach(tech => {
    const opt = document.createElement('option');
    opt.value = tech.name;
    opt.textContent = `${tech.name} (Tải ${tech.workload}% - ${tech.openTickets} việc)`;
    select.appendChild(opt);
  });

  document.getElementById('assignModal').classList.add('show');
};

function handleConfirmAssign() {
  const selectedTechName = document.getElementById('assignTechSelect').value;
  if (!selectedTechName) {
    alert('Vui lòng chọn kỹ thuật viên để phân công.');
    return;
  }

  const tickets = getStoredTickets();
  const ticket = tickets.find(t => t.id === pendingAssignTicketId);
  if (ticket) {
    ticket.assignedTech = selectedTechName;
    ticket.status = 'in_progress';
    ticket.history.push({
      time: new Date().toISOString().slice(0, 16).replace('T', ' '),
      title: 'Trưởng ban điều phối phân công',
      note: `Phân công sự cố cho KTV ${selectedTechName}.`,
      by: 'Ban Quản Lý (Admin)'
    });
    saveStoredTickets(tickets);

    // Tăng nhẹ workload KTV
    const teams = getTeamsData();
    const tech = teams[currentSelectedTeam].techs.find(t => t.name === selectedTechName);
    if (tech) {
      tech.openTickets++;
      tech.workload = Math.min(100, tech.workload + 20);
      saveTeamsData(teams);
    }

    alert(`Đã điều phối ticket #${ticket.id} cho KTV ${selectedTechName}!`);
    document.getElementById('assignModal').classList.remove('show');
    renderManagementDashboard();
  }
}

// Xử lý thêm KTV mới
function handleAddMember(e) {
  e.preventDefault();
  const name = document.getElementById('newTechName').value.trim();
  const email = document.getElementById('newTechEmail').value.trim();
  const phone = document.getElementById('newTechPhone').value.trim();
  const role = document.getElementById('newTechRole').value;

  if (!name || !email || !phone) {
    alert('Vui lòng điền đầy đủ các thông tin bắt buộc.');
    return;
  }

  const teams = getTeamsData();
  const team = teams[currentSelectedTeam];
  const nextId = `KV` + (team.techs.length + 1).toString().padStart(3, '0');

  team.techs.push({
    id: nextId,
    name: name,
    email: email,
    phone: phone,
    role: role,
    active: true,
    rating: '5.0',
    workload: 0,
    openTickets: 0
  });

  saveTeamsData(teams);
  alert(`Đã thêm thành công thành viên ${name} vào Đội ${currentSelectedTeam}!`);
  document.getElementById('addMemberModal').classList.remove('show');
  document.getElementById('addMemberForm').reset();
  renderManagementDashboard();
}
