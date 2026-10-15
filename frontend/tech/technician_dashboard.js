let currentActiveTicketId = null;
let currentTabFilter = 'all'; // 'all', 'my_work', 'team_queue'

let currentTech = {
  name: '',
  idNumber: '',
  email: '',
  team: ''
};

let dashboardData = null;


/* =========================================================
   API
   ========================================================= */

const API_BASE_URL = 'http://127.0.0.1:5000';


/* =========================================================
   AUTHORIZATION
   ========================================================= */

async function checkTechnicianAuth() {
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
      return false;
    }

    const user = result.data?.user;

    if (!user) {
      window.location.href = '../login/login.html';
      return false;
    }

    if (user.role !== 'TECHNICIAN') {
      alert('Bạn không có quyền truy cập trang này.');
      window.location.href = '../login/login.html';
      return false;
    }

    currentTech.name = user.name || '';
    currentTech.idNumber = user.id || '';
    currentTech.email = user.email || '';
    currentTech.team = user.team_id || '';

    return true;

  } catch (error) {
    console.error('Lỗi kiểm tra đăng nhập:', error);

    alert('Không thể kết nối đến server.');

    return false;
  }
}


/* =========================================================
   LOGOUT
   ========================================================= */

async function logout() {
  try {
    await fetch(
      `${API_BASE_URL}/auth/logout`,
      {
        method: 'POST',
        credentials: 'include'
      }
    );
  } catch (error) {
    console.error('Lỗi logout:', error);
  }

  window.location.href = '../login/login.html';
}


/* =========================================================
   LOAD TECHNICIAN DASHBOARD
   ========================================================= */

async function loadTechnicianDashboard() {
  try {
    const response = await fetch(
      `${API_BASE_URL}/technician/dashboard`,
      {
        method: 'GET',
        credentials: 'include'
      }
    );

    const result = await response.json();

    if (response.status === 401) {
      window.location.href = '../login/login.html';
      return;
    }

    if (response.status === 403) {
      alert(
        result.error?.message ||
        'Bạn không có quyền truy cập.'
      );

      window.location.href = '../login/login.html';
      return;
    }

    if (!response.ok || !result.success) {
      alert(
        result.error?.message ||
        'Không thể tải dữ liệu Technician Dashboard.'
      );

      return;
    }

    dashboardData = result.data;

    /*
     * Lấy thông tin Technician trực tiếp từ backend.
     * Backend trả về:
     *
     * tech_info
     * workload_stats
     * ticket_queue
     */

    if (dashboardData.tech_info) {
      currentTech.name =
        dashboardData.tech_info.name || currentTech.name;

      currentTech.idNumber =
        dashboardData.tech_info.id || currentTech.idNumber;

      currentTech.email =
        dashboardData.tech_info.email || currentTech.email;

      if (dashboardData.tech_info.team) {
        currentTech.team =
          dashboardData.tech_info.team.id || currentTech.team;
      }
    }

    renderTechHeader();
    renderTechDashboard();

  } catch (error) {
    console.error(
      'Lỗi tải Technician Dashboard:',
      error
    );

    alert(
      'Không thể kết nối đến server.'
    );
  }
}


/* =========================================================
   RENDER TECHNICIAN HEADER
   ========================================================= */

function renderTechHeader() {

  const techName =
    document.getElementById('techName');

  const techMetaInfo =
    document.getElementById('techMetaInfo');

  if (techName) {
    techName.textContent =
      currentTech.name;
  }

  if (techMetaInfo) {
    techMetaInfo.textContent =
      `Mã: ${currentTech.idNumber} • Team: ${currentTech.team}`;
  }
}


/* =========================================================
   DOM CONTENT LOADED
   ========================================================= */

document.addEventListener(
  'DOMContentLoaded',
  async () => {

    // =====================================================
    // Authentication + Authorization
    // =====================================================

    const isAuthenticated =
      await checkTechnicianAuth();

    if (!isAuthenticated) {
      return;
    }


    // =====================================================
    // Header
    // =====================================================

    renderTechHeader();


    // =====================================================
    // Sidebar
    // =====================================================

    setupSidebarNavigation();


    // =====================================================
    // Load Dashboard từ Database
    // =====================================================

    await loadTechnicianDashboard();


    // =====================================================
    // Search
    // =====================================================

    const searchInput =
      document.getElementById('searchInput');

    if (searchInput) {
      searchInput.addEventListener(
        'input',
        renderTechDashboard
      );
    }


    // =====================================================
    // Filter Status
    // =====================================================

    const filterStatus =
      document.getElementById('filterStatus');

    if (filterStatus) {
      filterStatus.addEventListener(
        'change',
        renderTechDashboard
      );
    }


    // =====================================================
    // Filter Priority
    // =====================================================

    const filterPriority =
      document.getElementById('filterPriority');

    if (filterPriority) {
      filterPriority.addEventListener(
        'change',
        renderTechDashboard
      );
    }


    // =====================================================
    // Filter Building
    // =====================================================

    const filterBuilding =
      document.getElementById('filterBuilding');

    if (filterBuilding) {
      filterBuilding.addEventListener(
        'change',
        renderTechDashboard
      );
    }


    // =====================================================
    // Logout
    // =====================================================

    const btnLogout =
      document.getElementById('btnLogout');

    if (btnLogout) {
      btnLogout.addEventListener(
        'click',
        logout
      );
    }


    // =====================================================
    // Modal Close
    // =====================================================

    const modal =
      document.getElementById('techTicketModal');

    const btnModalClose =
      document.getElementById('btnModalClose');

    if (btnModalClose) {
      btnModalClose.addEventListener(
        'click',
        () => {
          modal.classList.remove('show');
        }
      );
    }

    if (modal) {
      modal.addEventListener(
        'click',
        (e) => {
          if (e.target === modal) {
            modal.classList.remove('show');
          }
        }
      );
    }


    // =====================================================
    // Lưu ghi chú nội bộ
    // =====================================================

    const btnSaveInternalNote =
      document.getElementById(
        'btnSaveInternalNote'
      );

    if (btnSaveInternalNote) {
      btnSaveInternalNote.addEventListener(
        'click',
        saveInternalNote
      );
    }


    // =====================================================
    // Resolve
    // =====================================================

    const btnMarkResolved =
      document.getElementById(
        'btnMarkResolved'
      );

    if (btnMarkResolved) {
      btnMarkResolved.addEventListener(
        'click',
        resolveTicket
      );
    }


    // =====================================================
    // Escalate
    // =====================================================

    const btnEscalate =
      document.getElementById(
        'btnEscalate'
      );

    if (btnEscalate) {
      btnEscalate.addEventListener(
        'click',
        escalateTicket
      );
    }

  }
);


/* =========================================================
   SIDEBAR NAVIGATION
   ========================================================= */

function setupSidebarNavigation() {

  const navAll =
    document.querySelector(
      '.sidebar-nav .nav-item:nth-child(1)'
    );

  const navMyWork =
    document.getElementById('navMyWork');

  const navTeamQueue =
    document.getElementById('navTeamQueue');

  const allNavs = [
    navAll,
    navMyWork,
    navTeamQueue
  ];


  function setActive(
    activeEl,
    tabType
  ) {

    allNavs.forEach(el => {

      if (el) {
        el.classList.remove('active');
      }

    });

    if (activeEl) {
      activeEl.classList.add('active');
    }

    currentTabFilter =
      tabType;

    renderTechDashboard();
  }


  if (navAll) {
    navAll.addEventListener(
      'click',
      (e) => {

        e.preventDefault();

        setActive(
          navAll,
          'all'
        );

      }
    );
  }


  if (navMyWork) {
    navMyWork.addEventListener(
      'click',
      (e) => {

        e.preventDefault();

        setActive(
          navMyWork,
          'my_work'
        );

      }
    );
  }


  if (navTeamQueue) {
    navTeamQueue.addEventListener(
      'click',
      (e) => {

        e.preventDefault();

        setActive(
          navTeamQueue,
          'team_queue'
        );

      }
    );
  }
}


/* =========================================================
   RENDER TECHNICIAN DASHBOARD
   ========================================================= */

function renderTechDashboard() {

  if (!dashboardData) {
    return;
  }


  const tickets =
    dashboardData.ticket_queue || [];


  const workloadStats = dashboardData.workload_stats || {
    assigned: 0,
    in_progress: 0,
    waiting_confirm: 0,
    re_process: 0,
  };

  const elAssign  = document.getElementById('statAssigned');
  const elProg    = document.getElementById('statProgress');
  const elWaiting = document.getElementById('statWaitingConfirm');

  if (elAssign)  elAssign.textContent  = workloadStats.assigned || 0;
  if (elProg)    elProg.textContent    = workloadStats.in_progress || 0;
  if (elWaiting) elWaiting.textContent = workloadStats.waiting_confirm || 0;


  // =======================================================
  // 2. Search & Filter
  // =======================================================

  const searchInput =
    document.getElementById(
      'searchInput'
    );

  const filterStatus =
    document.getElementById(
      'filterStatus'
    );

  const filterPriority =
    document.getElementById(
      'filterPriority'
    );

  const filterBuilding =
    document.getElementById(
      'filterBuilding'
    );


  const q =
    searchInput
      ? searchInput.value.toLowerCase().trim()
      : '';


  const fStatus =
    filterStatus
      ? filterStatus.value
      : 'all';


  const fPriority =
    filterPriority
      ? filterPriority.value
      : 'all';


  const fBuilding =
    filterBuilding
      ? filterBuilding.value
      : 'all';


  // =======================================================
  // 3. Filter tickets
  // =======================================================

  const filtered =
    tickets.filter(ticket => {

      /*
       * Backend trả status dạng:
       *
       * ASSIGNED
       * IN_PROGRESS
       * RESOLVED
       */

      const status =
        (ticket.status || '').toLowerCase();


      // ---------------------------------------------------
      // Tab "Việc tôi phụ trách"
      // ---------------------------------------------------

      if (currentTabFilter === 'my_work') {
        if (ticket.assigned_to !== currentTech.idNumber) {
          return false;
        }
      }


      // ---------------------------------------------------
      // Tab "Hàng đợi của Team"
      // ---------------------------------------------------

      if (currentTabFilter === 'team_queue') {

        /*
         * Backend get_technician_ticket_queue()
         * đã giới hạn ticket theo Team của Technician.
         *
         * Vì vậy ở đây không cần kiểm tra lại Team.
         */
      }


      // ---------------------------------------------------
      // Search
      // ---------------------------------------------------

      const reporterName =
        ticket.reporter?.name || '';

      const buildingName =
        ticket.location?.building?.name || '';

      const roomName =
        ticket.location?.room?.name || '';

      const location =
        `${buildingName} ${roomName}`;


      const title =
        ticket.title || '';


      const ticketId =
        ticket.id || '';


      const matchQ =
        ticketId
          .toLowerCase()
          .includes(q) ||

        reporterName
          .toLowerCase()
          .includes(q) ||

        location
          .toLowerCase()
          .includes(q) ||

        title
          .toLowerCase()
          .includes(q);


      // ---------------------------------------------------
      // Status
      // ---------------------------------------------------

      const matchStatus =
        fStatus === 'all' ||
        status === fStatus.toLowerCase();


      // ---------------------------------------------------
      // Priority
      // ---------------------------------------------------

      const priority =
        (ticket.priority || '').toLowerCase();

      const matchPriority =
        fPriority === 'all' ||
        priority === fPriority.toLowerCase();


      // ---------------------------------------------------
      // Building
      // ---------------------------------------------------

      const matchBuilding =
        fBuilding === 'all' ||
        buildingName
          .toLowerCase()
          .includes(
            fBuilding.toLowerCase()
          );


      return (
        matchQ &&
        matchStatus &&
        matchPriority &&
        matchBuilding
      );

    });


  // =======================================================
  // 4. Subtitle
  // =======================================================

  const subtitleEl =
    document.querySelector(
      '.table-subtitle'
    );


  if (subtitleEl) {

    if (currentTabFilter === 'my_work') {

      subtitleEl.textContent =
        `Đang hiển thị danh sách sự cố do bạn (${currentTech.name}) trực tiếp xử lý`;

    } else if (
      currentTabFilter === 'team_queue'
    ) {

      subtitleEl.textContent =
        `Đang hiển thị hàng đợi sự cố thuộc Team ${currentTech.team}`;

    } else {

      subtitleEl.textContent =
        'Nhấp vào dòng để mở màn hình chi tiết xử lý kỹ thuật';

    }

  }


  // =======================================================
  // 5. Render Table
  // =======================================================

  const tbody =
    document.getElementById(
      'techTicketsTableBody'
    );


  if (!tbody) {
    return;
  }


  tbody.innerHTML = '';


  if (filtered.length === 0) {

    const tr =
      document.createElement('tr');

    tr.innerHTML = `
      <td
        colspan="8"
        style="
          text-align:center;
          padding:30px;
          color:#94a3b8;
        "
      >
        Không có sự cố nào trong danh mục này.
      </td>
    `;

    tbody.appendChild(tr);

    return;
  }


  filtered.forEach(ticket => {

    const tr =
      document.createElement('tr');


    tr.className =
      'clickable-row';


    const status =
      (ticket.status || '').toLowerCase();


    // =====================================================
    // Reporter
    // =====================================================

    const reporter =
      ticket.reporter?.name ||
      'Không xác định';


    // =====================================================
    // Location
    // =====================================================

    const building =
      ticket.location?.building?.name ||
      '';


    const room =
      ticket.location?.room?.name ||
      '';


    const location =
      `${building}${room ? ' - ' + room : ''}`;


    // =====================================================
    // Team
    // =====================================================

    const team =
      currentTech.team ||
      '';


    // =====================================================
    // Technician
    // =====================================================

    let assignedTech =
      'Chưa phân công';


    /*
     * Dashboard API hiện tại không trả assigned_to.
     *
     * Với IN_PROGRESS/RESOLVED, tên Technician hiện tại
     * được dùng để hiển thị.
     */

    if (ticket.assigned_to) {
      assignedTech = (ticket.assigned_to === currentTech.idNumber)
        ? currentTech.name
        : ticket.assigned_to;
    }

    // =====================================================
    // Action Button
    // =====================================================

    let actionBtnHtml = '';


    if (status === 'assigned'|| status === 're_process') {

      actionBtnHtml = `
        <button
          class="btn-action-primary btn-claim"
          data-id="${ticket.id}">
          Nhận xử lý
        </button>
      `;

    } else {

      actionBtnHtml = `
        <span
          style="
            font-size:12px;
            color:#64748b;
          "
        >
          Đang theo dõi
        </span>
      `;

    }


    // =====================================================
    // Row
    // =====================================================

    tr.innerHTML = `
      <td>
        <strong>#${ticket.id}</strong>
      </td>

      <td>
        ${reporter}
      </td>

      <td>
        ${location}
      </td>

      <td>
        ${ticket.title || 'Không có tiêu đề'}
      </td>

      <td>
        <span class="priority-${ticket.priority}">
          ${getPriorityLabel(
            ticket.priority
          )}
        </span>
      </td>

      <td>
        <span class="badge badge-${status}">
          ${getStatusLabel(status)}
        </span>
      </td>

      <td>
        <strong>${assignedTech}</strong>
        (${team})
      </td>

      <td>
        ${actionBtnHtml}
      </td>
    `;


    // =====================================================
    // Click row
    // =====================================================

    tr.addEventListener(
      'click',
      (e) => {

        if (
          !e.target.closest('.btn-claim')
        ) {

          openTechTicketDetail(
            ticket.id
          );

        }

      }
    );


    tbody.appendChild(tr);

  });


  // =======================================================
  // 6. Claim buttons
  // =======================================================

  document
    .querySelectorAll('.btn-claim')
    .forEach(btn => {

      btn.addEventListener(
        'click',
        (e) => {

          e.stopPropagation();

          const ticketId =
            btn.getAttribute('data-id');

          claimTicket(ticketId);

        }
      );

    });

}


/* =========================================================
   CLAIM TICKET
   ========================================================= */

async function claimTicket(ticketId) {

  try {

    const response =
      await fetch(
        `${API_BASE_URL}/technician/tickets/${ticketId}/accept`,
        {
          method: 'POST',
          credentials: 'include'
        }
      );


    const result =
      await response.json();


    if (response.status === 401) {

      window.location.href =
        '../login/login.html';

      return;
    }


    if (!response.ok || !result.success) {

      alert(
        result.error?.message ||
        'Không thể nhận xử lý ticket.'
      );

      return;
    }


    alert(
      `Bạn đã nhận xử lý ticket #${ticketId}! Trạng thái chuyển sang "Đang xử lý".`
    );


    // Load lại dữ liệu từ Database
    await loadTechnicianDashboard();


  } catch (error) {

    console.error(
      'Lỗi nhận xử lý ticket:',
      error
    );

    alert(
      'Không thể kết nối đến server.'
    );

  }

}


/* =========================================================
   TICKET DETAIL
   ========================================================= */

async function openTechTicketDetail(ticketId) {

  currentActiveTicketId =
    ticketId;


  try {

    const response =
      await fetch(
        `${API_BASE_URL}/technician/tickets/${ticketId}`,
        {
          method: 'GET',
          credentials: 'include'
        }
      );


    const result =
      await response.json();


    if (response.status === 401) {

      window.location.href =
        '../login/login.html';

      return;
    }


    if (!response.ok || !result.success) {

      alert(
        result.error?.message ||
        'Không thể tải chi tiết ticket.'
      );

      return;
    }


    const data =
      result.data;


    const ticket =
      data.ticket_summary;


    if (!ticket) {

      alert(
        'Không tìm thấy thông tin ticket.'
      );

      return;
    }


    // =====================================================
    // Basic information
    // =====================================================

    document.getElementById(
      'modalTitle'
    ).textContent =
      ticket.title ||
      'Chi tiết ticket';


    document.getElementById(
      'modalTicketId'
    ).textContent =
      '#' + ticket.id;


    document.getElementById(
      'modalPriority'
    ).textContent =
      getPriorityLabel(
        ticket.priority
      );


    document.getElementById(
      'modalReporter'
    ).textContent =
      ticket.reporter?.name ||
      'Không xác định';


    // =====================================================
    // Location
    // =====================================================

    const building =
      ticket.location?.building?.name ||
      '';


    const room =
      ticket.location?.room?.name ||
      '';


    document.getElementById(
      'modalLocation'
    ).textContent =
      `${building}${room ? ' - ' + room : ''}`;


    // =====================================================
    // Team
    // =====================================================

    document.getElementById(
      'modalTeam'
    ).textContent =
      currentTech.team;


    // =====================================================
    // Description
    // =====================================================

    document.getElementById(
      'modalDescription'
    ).textContent =
      ticket.description ||
      '';


    // =====================================================
    // Internal notes
    // =====================================================

    const internalNotes =
      data.internal_notes || [];


    const internalNotesInput =
      document.getElementById(
        'internalNotesInput'
      );


    if (internalNotesInput) {

      if (Array.isArray(internalNotes)) {

        internalNotesInput.value =
          internalNotes
            .map(note => {

              if (
                typeof note === 'string'
              ) {
                return note;
              }

              return note.note || '';

            })
            .filter(Boolean)
            .join('\n');

      } else {

        internalNotesInput.value =
          internalNotes || '';

      }

    }


    // =====================================================
    // Timeline
    // =====================================================

    const timeline =
      document.getElementById(
        'techModalTimeline'
      );


    if (timeline) {

      timeline.innerHTML = '';


      const activityLog =
        data.activity_log || [];


      if (activityLog.length === 0) {

        timeline.innerHTML = `
          <div
            style="
              color:#94a3b8;
              padding:15px;
            "
          >
            Chưa có lịch sử xử lý.
          </div>
        `;

      } else {

        activityLog.forEach(item => {

          const div =
            document.createElement(
              'div'
            );


          div.className =
            'timeline-item';


          const oldStatus =
            item.old_status ||
            '—';


          const newStatus =
            item.new_status ||
            '—';


          const note =
            item.note ||
            '';


          const updatedBy =
            item.updated_by ||
            '';


          div.innerHTML = `
            <div class="timeline-dot"></div>

            <span class="timeline-time">
              ${formatBackendDate(item.time)}
              • bởi
              <strong>${updatedBy}</strong>
            </span>

            <div class="timeline-content">

              <strong>
                ${getStatusLabel(
                  newStatus
                )}
              </strong>

              <p>
                ${oldStatus}
                → ${newStatus}
              </p>

              ${
                note
                  ? `<p>${formatNote(note)}</p>`
                  : ''
              }

            </div>
          `;


          timeline.appendChild(div);

        });

      }

    }


    // =====================================================
    // Resolve form
    // =====================================================

    const resolveBox =
      document.getElementById(
        'resolveFormBox'
      );


    const status =
      (ticket.status || '')
        .toLowerCase();


    if (resolveBox) {

      if (
        status === 'resolved' ||
        status === 'closed'
      ) {

        resolveBox.style.display =
          'none';

      } else {

        resolveBox.style.display =
          'block';

      }

    }


    // =====================================================
    // Show modal
    // =====================================================

    document
      .getElementById(
        'techTicketModal'
      )
      .classList.add('show');


  } catch (error) {

    console.error(
      'Lỗi tải chi tiết ticket:',
      error
    );

    alert(
      'Không thể kết nối đến server.'
    );

  }

}


/* =========================================================
   SAVE INTERNAL NOTE / UPDATE PROGRESS
   ========================================================= */

async function saveInternalNote() {

  if (!currentActiveTicketId) {

    alert(
      'Chưa chọn ticket.'
    );

    return;
  }


  const input =
    document.getElementById(
      'internalNotesInput'
    );


  const noteText =
    input
      ? input.value.trim()
      : '';


  if (!noteText) {

    alert(
      'Vui lòng nhập nội dung ghi chú nội bộ.'
    );

    return;
  }


  try {

    const response =
      await fetch(
        `${API_BASE_URL}/technician/tickets/${currentActiveTicketId}/progress`,
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json'
          },

          credentials: 'include',

          body: JSON.stringify({
            note: noteText
          })
        }
      );


    const result =
      await response.json();


    if (response.status === 401) {

      window.location.href =
        '../login/login.html';

      return;
    }


    if (!response.ok || !result.success) {

      alert(
        result.error?.message ||
        'Không thể cập nhật tiến độ.'
      );

      return;
    }


    alert(
      'Đã lưu cập nhật tiến độ thành công!'
    );


    await openTechTicketDetail(
      currentActiveTicketId
    );


    await loadTechnicianDashboard();


  } catch (error) {

    console.error(
      'Lỗi cập nhật tiến độ:',
      error
    );

    alert(
      'Không thể kết nối đến server.'
    );

  }

}


/* =========================================================
   RESOLVE TICKET
   ========================================================= */

async function resolveTicket() {

  if (!currentActiveTicketId) {

    alert(
      'Chưa chọn ticket.'
    );

    return;
  }


  const rootCause =
    document
      .getElementById(
        'rootCauseInput'
      )
      .value
      .trim();


  const solution =
    document
      .getElementById(
        'solutionInput'
      )
      .value
      .trim();


  if (!rootCause || !solution) {

    alert(
      'Yêu cầu bắt buộc: Vui lòng nhập đầy đủ Nguyên nhân sự cố và Giải pháp khắc phục trước khi Resolve.'
    );

    return;
  }


  try {

    const response =
      await fetch(
        `${API_BASE_URL}/technician/tickets/${currentActiveTicketId}/resolve`,
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json'
          },

          credentials: 'include',

          body: JSON.stringify({
            cause: rootCause,
            solution: solution
          })
        }
      );


    const result =
      await response.json();


    if (response.status === 401) {

      window.location.href =
        '../login/login.html';

      return;
    }


    if (!response.ok || !result.success) {

      alert(
        result.error?.message ||
        'Không thể Resolve ticket.'
      );

      return;
    }


    alert(
      `Đã hoàn tất xử lý ticket #${currentActiveTicketId}! Trạng thái chuyển sang "Resolved" để chờ người dùng nghiệm thu.`
    );


    // Xóa nội dung form
    document.getElementById(
      'rootCauseInput'
    ).value = '';


    document.getElementById(
      'solutionInput'
    ).value = '';


    // Reload dashboard
    await loadTechnicianDashboard();


    // Reload detail
    await openTechTicketDetail(
      currentActiveTicketId
    );


  } catch (error) {

    console.error(
      'Lỗi Resolve ticket:',
      error
    );

    alert(
      'Không thể kết nối đến server.'
    );

  }

}


/* =========================================================
   ESCALATE TICKET
   ========================================================= */

async function escalateTicket() {

  if (!currentActiveTicketId) {

    alert(
      'Chưa chọn ticket.'
    );

    return;
  }


  const newTeam =
    document
      .getElementById(
        'escalateTeamSelect'
      )
      .value;


  const reason =
    document
      .getElementById(
        'escalateReasonInput'
      )
      .value
      .trim();


  if (!newTeam) {

    alert(
      'Vui lòng chọn Team cần chuyển.'
    );

    return;
  }


  if (!reason) {

    alert(
      'Vui lòng nhập lý do chuyển tiếp Team.'
    );

    return;
  }


  try {

    const response =
      await fetch(
        `${API_BASE_URL}/technician/tickets/${currentActiveTicketId}/escalate`,
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json'
          },

          credentials: 'include',

          body: JSON.stringify({
            new_team_id: newTeam,
            reason: reason
          })
        }
      );


    const result =
      await response.json();


    if (response.status === 401) {

      window.location.href =
        '../login/login.html';

      return;
    }


    if (!response.ok || !result.success) {

      alert(
        result.error?.message ||
        'Không thể chuyển Team.'
      );

      return;
    }


    alert(
      `Đã chuyển ticket #${currentActiveTicketId} sang Team ${newTeam}!`
    );


    // Xóa form
    document.getElementById(
      'escalateReasonInput'
    ).value = '';


    // Reload dashboard
    await loadTechnicianDashboard();


    // Reload detail
    await openTechTicketDetail(
      currentActiveTicketId
    );


  } catch (error) {

    console.error(
      'Lỗi Escalate ticket:',
      error
    );

    alert(
      'Không thể kết nối đến server.'
    );

  }

}


/* =========================================================
   DATE FORMAT
   ========================================================= */

function formatBackendDate(value) {

  if (!value) {
    return '';
  }


  const date =
    new Date(value);


  if (Number.isNaN(
    date.getTime()
  )) {

    return value;
  }


  return date.toLocaleString(
    'vi-VN',
    {
      dateStyle: 'short',
      timeStyle: 'medium'
    }
  );

}


/* =========================================================
   NOTE FORMAT
   ========================================================= */

function formatNote(note) {

  if (!note) {
    return '';
  }


  return String(note)
    .replace(
      /\n/g,
      '<br>'
    );

}


/* =========================================================
   LABEL HELPERS
   ========================================================= */

function getPriorityLabel(priority) {

  const map = {

    critical:
      'Khẩn cấp',

    high:
      'Cao',

    medium:
      'Trung bình',

    low:
      'Thấp'

  };


  return map[
    String(priority).toLowerCase()
  ] || priority || '';

}


function getStatusLabel(status) {
  const map = {
    new:              'Mới tạo',
    assigned:         'Chờ tiếp nhận',
    in_progress:      'Đang xử lý',
    waiting_confirm:  'Chờ nghiệm thu',
    re_process:       'Cần xử lý lại',
    closed:           'Đã đóng',
    cancelled:        'Đã hủy',
  };
  return map[String(status).toLowerCase()] || status || '';
}