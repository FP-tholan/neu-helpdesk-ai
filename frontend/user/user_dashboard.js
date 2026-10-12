const SHARED_STORAGE_KEY = 'neu_helpdesk_shared_tickets';

const DEFAULT_USER_TICKETS = [
  {
    id: 'TCK-2026-001',
    reporter: 'Nguyễn Văn An (SV)',
    title: 'Máy chiếu phòng B102 không lên tín hiệu',
    category: 'Thiết bị giảng dạy / Máy chiếu',
    priority: 'high',
    status: 'in_progress',
    createdAt: '2026-09-28 08:30',
    location: 'Nhà B - Phòng 102',
    building: 'Nhà B',
    assignedTeam: 'T_QTTB',
    assignedTech: 'Lê Hoàng Long',
    description: 'Bật nguồn máy chiếu có đèn nhưng màn chiếu không nhận cổng HDMI từ laptop giảng viên.',
    history: [
      {
        time: '2026-09-28 08:30',
        title: 'Tạo ticket thành công',
        note: 'Người dùng gửi báo cáo sự cố qua hệ thống.',
        by: 'Nguyễn Văn An'
      },
      {
        time: '2026-09-28 08:45',
        title: 'Tiếp nhận xử lý',
        note: 'Phân công cho Team T_QTTB (KTV Lê Hoàng Long).',
        by: 'HelpDesk Dispatcher'
      }
    ]
  },
  {
    id: 'TCK-2026-002',
    reporter: 'Trần Thị Bình (GV)',
    title: 'Mạng Wi-Fi NEU-Student chập chờn tại sảnh A1',
    category: 'Mạng & Hạ tầng CNTT',
    priority: 'medium',
    status: 'assigned',
    createdAt: '2026-09-29 10:15',
    location: 'Nhà A1 - Sảnh chính tầng 1',
    building: 'Nhà A1',
    assignedTeam: 'T_IT',
    assignedTech: 'Chưa phân công',
    description: 'Sinh viên không thể kết nối hoặc liên tục bị ngắt kết nối khi đang học trực tuyến.',
    history: [
      {
        time: '2026-09-29 10:15',
        title: 'Tạo ticket',
        note: 'Yêu cầu hỗ trợ hạ tầng mạng.',
        by: 'Trần Thị Bình'
      }
    ]
  },
  {
    id: 'TCK-2026-003',
    reporter: 'Ban Tổ Chức Hội Thảo',
    title: 'Micro không dây phòng hội trường A2 bị rè',
    category: 'Âm thanh & Ánh sáng',
    priority: 'critical',
    status: 'assigned',
    createdAt: '2026-09-30 08:00',
    location: 'Hội trường A2',
    building: 'Hội trường A2',
    assignedTeam: 'T_PSA',
    assignedTech: 'Chưa phân công',
    description: 'Micro số 1 và số 2 bị nhiễu sóng và rè khi nói to.',
    history: [
      {
        time: '2026-09-30 08:00',
        title: 'Tạo ticket khẩn cấp',
        note: 'Cần xử lý trước giờ hội thảo chiều nay.',
        by: 'Ban Tổ Chức'
      }
    ]
  },
  {
    id: 'TCK-2026-004',
    reporter: 'Nguyễn Văn An (SV)',
    title: 'Điều hòa phòng C301 không mát và rỉ nước',
    category: 'Điện lạnh & CSVC',
    priority: 'low',
    status: 'resolved',
    createdAt: '2026-09-20 14:00',
    location: 'Nhà C - Phòng 301',
    building: 'Nhà C',
    assignedTeam: 'T_QTTB',
    assignedTech: 'Lê Hoàng Long',
    description: 'Điều hòa nhiệt độ cài 18 độ nhưng phòng vẫn nóng, có nước nhỏ giọt xuống sàn.',
    history: [
      {
        time: '2026-09-20 14:00',
        title: 'Tạo ticket',
        note: 'Báo lỗi điều hòa.',
        by: 'Nguyễn Văn An'
      },
      {
        time: '2026-09-20 16:30',
        title: 'Đã xử lý xong (Resolved)',
        note: 'Đã bảo dưỡng và nạp ga hoàn chỉnh.',
        by: 'Lê Hoàng Long'
      }
    ]
  }
];


// ============================================================
// LOCAL STORAGE - TẠM THỜI
// Không sử dụng cho Create Ticket và Ticket Detail.
// ============================================================

function getStoredTickets() {

  const data =
    localStorage.getItem(
      SHARED_STORAGE_KEY
    );

  if (!data) {

    localStorage.setItem(
      SHARED_STORAGE_KEY,
      JSON.stringify(DEFAULT_USER_TICKETS)
    );

    return DEFAULT_USER_TICKETS;
  }

  try {

    return JSON.parse(data);

  } catch (e) {

    console.error(
      'Không thể đọc localStorage:',
      e
    );

    return DEFAULT_USER_TICKETS;
  }
}


function saveStoredTickets(tickets) {

  localStorage.setItem(
    SHARED_STORAGE_KEY,
    JSON.stringify(tickets)
  );
}


// ============================================================
// FORMAT TIME
// ============================================================

function formatNow() {

  const d = new Date();

  return d
    .toISOString()
    .slice(0, 16)
    .replace('T', ' ');
}


// ============================================================
// CURRENT USER
// ============================================================

let currentUser = {
  name: '',
  email: '',
  id: '',
  role: 'USER'
};


// ============================================================
// CHECK USER AUTHORIZATION
// ============================================================

async function checkUserAuth() {

  try {

    const response =
      await fetch(
        'http://127.0.0.1:5000/auth/me',
        {
          method: 'GET',
          credentials: 'include'
        }
      );

    const result =
      await response.json();


    // --------------------------------------------------------
    // CHƯA ĐĂNG NHẬP
    // --------------------------------------------------------

    if (!response.ok) {

      window.location.href =
        '../login/login.html';

      return false;
    }


    const user =
      result.data?.user;


    // --------------------------------------------------------
    // KHÔNG PHẢI USER
    // --------------------------------------------------------

    if (!user || user.role !== 'USER') {

      alert(
        'Bạn không có quyền truy cập trang này.'
      );

      window.location.href =
        '../login/login.html';

      return false;
    }


    // --------------------------------------------------------
    // LƯU THÔNG TIN USER
    // --------------------------------------------------------

    currentUser = {

      name:
        user.name,

      email:
        user.email,

      id:
        user.id,

      role:
        user.role
    };


    return true;

  } catch (error) {

    console.error(
      'Check user auth error:',
      error
    );

    alert(
      'Không thể kết nối đến Backend.'
    );

    return false;
  }
}


// ============================================================
// LOAD DASHBOARD FROM BACKEND
// ============================================================

async function loadDashboardData() {

  try {

    const response =
      await fetch(
        'http://127.0.0.1:5000/api/dashboard',
        {
          method: 'GET',
          credentials: 'include'
        }
      );


    const result =
      await response.json();


    if (!response.ok || !result.success) {

      if (response.status === 401) {

        alert(
          'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.'
        );

        window.location.href =
          '../login/login.html';

        return;
      }


      alert(
        result.error?.message ||
        'Không thể tải dữ liệu Dashboard.'
      );

      return;
    }


    const dashboard =
      result.data;


    // --------------------------------------------------------
    // USER INFO
    // --------------------------------------------------------

    if (dashboard.user_info) {

      currentUser = {

        name:
          dashboard.user_info.name,

        email:
          dashboard.user_info.email,

        id:
          dashboard.user_info.id,

        role:
          'USER'
      };


      renderUserInfo(
        dashboard.user_info
      );
    }


    // --------------------------------------------------------
    // STATS
    // --------------------------------------------------------

    renderStatsFromBackend(
      dashboard.ticket_stats
    );


    // --------------------------------------------------------
    // RECENT TICKETS
    // --------------------------------------------------------

    renderTicketsTableFromBackend(
      dashboard.recent_tickets
    );

  } catch (error) {

    console.error(
      'Load Dashboard error:',
      error
    );

    alert(
      'Không thể kết nối đến Backend. Vui lòng kiểm tra server.'
    );
  }
}


// ============================================================
// RENDER USER INFO
// ============================================================

function renderUserInfo(userInfo) {

  const userNameEl =
    document.getElementById(
      'userName'
    );

  const userMetaEl =
    document.getElementById(
      'userMetaInfo'
    );

  const userAvatarEl =
    document.getElementById(
      'userAvatar'
    );


  if (userNameEl) {

    userNameEl.textContent =
      userInfo.name;
  }


  if (userMetaEl) {

    userMetaEl.textContent =
      userInfo.email;
  }


  if (userAvatarEl && userInfo.name) {

    const words =
      userInfo.name
        .trim()
        .split(' ');

    userAvatarEl.textContent =
      words[words.length - 1]
        .substring(0, 2)
        .toUpperCase();
  }
}


// ============================================================
// DOM CONTENT LOADED
// ============================================================

document.addEventListener(
  'DOMContentLoaded',
  async () => {


    // --------------------------------------------------------
    // CHECK AUTHORIZATION
    // --------------------------------------------------------

    const isAuthenticated =
      await checkUserAuth();


    if (!isAuthenticated) {
      return;
    }


    // --------------------------------------------------------
    // LOAD DASHBOARD FROM BACKEND
    // --------------------------------------------------------

    await loadDashboardData();


    // --------------------------------------------------------
    // ĐĂNG XUẤT
    // --------------------------------------------------------

    const btnLogout =
      document.getElementById(
        'btnLogout'
      );


    if (btnLogout) {

      btnLogout.addEventListener(
        'click',
        async () => {

          try {

            await fetch(
              'http://127.0.0.1:5000/auth/logout',
              {
                method: 'POST',
                credentials: 'include'
              }
            );

          } catch (error) {

            console.error(
              'Logout error:',
              error
            );

          } finally {

            window.location.href =
              '../login/login.html';
          }

        }
      );
    }


    // --------------------------------------------------------
    // MODAL TẠO TICKET
    // --------------------------------------------------------

    const createModal =
      document.getElementById(
        'createTicketModal'
      );

    const btnNewTicket =
      document.getElementById(
        'btnNewTicket'
      );

    const btnSidebarNewTicket =
      document.getElementById(
        'btnSidebarNewTicket'
      );

    const btnCreateModalClose =
      document.getElementById(
        'btnCreateModalClose'
      );

    const btnCancelCreate =
      document.getElementById(
        'btnCancelCreate'
      );


    function openCreateModal() {

      if (createModal) {

        createModal.classList.add(
          'show'
        );
      }
    }


    function closeCreateModal() {

      if (createModal) {

        createModal.classList.remove(
          'show'
        );
      }


      const form =
        document.getElementById(
          'createTicketForm'
        );


      if (form) {

        form.reset();
      }
    }


    if (btnNewTicket) {

      btnNewTicket.addEventListener(
        'click',
        openCreateModal
      );
    }


    if (btnSidebarNewTicket) {

      btnSidebarNewTicket.addEventListener(
        'click',
        (e) => {

          e.preventDefault();

          openCreateModal();
        }
      );
    }


    if (btnCreateModalClose) {

      btnCreateModalClose.addEventListener(
        'click',
        closeCreateModal
      );
    }


    if (btnCancelCreate) {

      btnCancelCreate.addEventListener(
        'click',
        closeCreateModal
      );
    }


    if (createModal) {

      createModal.addEventListener(
        'click',
        (e) => {

          if (e.target === createModal) {

            closeCreateModal();
          }
        }
      );
    }


    // ========================================================
    // CREATE TICKET - BACKEND API
    // ========================================================

    const createForm =
      document.getElementById(
        'createTicketForm'
      );


    if (createForm) {

      createForm.addEventListener(
        'submit',
        async (e) => {

          e.preventDefault();


          // --------------------------------------------------
          // LẤY DỮ LIỆU FORM
          // --------------------------------------------------

          const title =
            document.getElementById(
              'newTitle'
            )
              .value
              .trim();


          const building =
            document.getElementById(
              'newBuilding'
            )
              .value;


          const room =
            document.getElementById(
              'newRoom'
            )
              .value
              .trim();


          const category =
            document.getElementById(
              'newCategory'
            )
              .value;


          const priority =
            document.getElementById(
              'newPriority'
            )
              .value;


          const description =
            document.getElementById(
              'newDescription'
            )
              .value
              .trim();


          // --------------------------------------------------
          // VALIDATION
          // --------------------------------------------------

          if (
            !title ||
            !building ||
            !room ||
            !category ||
            !priority ||
            !description
          ) {

            alert(
              'Vui lòng điền đầy đủ các thông tin bắt buộc (*).'
            );

            return;
          }


          try {

            // ------------------------------------------------
            // GỌI BACKEND
            // ------------------------------------------------

            const response =
              await fetch(
                'http://127.0.0.1:5000/tickets',
                {
                  method: 'POST',

                  headers: {
                    'Content-Type':
                      'application/json'
                  },

                  credentials:
                    'include',

                  body:
                    JSON.stringify({

                      title:
                        title,

                      building:
                        building,

                      room:
                        room,

                      category:
                        category,

                      priority:
                        priority.toUpperCase(),

                      description:
                        description
                    })
                }
              );


            const result =
              await response.json();


            // ------------------------------------------------
            // BACKEND TRẢ LỖI
            // ------------------------------------------------

            if (
              !response.ok ||
              !result.success
            ) {

              alert(
                result.error?.message ||
                'Không thể tạo ticket. Vui lòng thử lại.'
              );

              return;
            }


            // ------------------------------------------------
            // TẠO THÀNH CÔNG
            // ------------------------------------------------

            const ticket =
              result.data;


            console.log(
              'Ticket được tạo bởi Backend:',
              ticket
            );


            alert(
              `Tạo yêu cầu hỗ trợ #${ticket.id} thành công! Kỹ thuật viên sẽ sớm tiếp nhận.`
            );


            closeCreateModal();


            // ------------------------------------------------
            // KHÔNG GHI LOCAL STORAGE
            // Ticket đã được lưu trong DATABASE
            // ------------------------------------------------

            await loadDashboardData();

          } catch (error) {

            console.error(
              'Create ticket error:',
              error
            );

            alert(
              'Không thể kết nối đến server. Vui lòng kiểm tra Backend.'
            );
          }

        }
      );
    }


    // --------------------------------------------------------
    // QUICK ACTION AI
    // --------------------------------------------------------

    const btnChatAi =
      document.getElementById(
        'btnChatAi'
      );

    const btnSidebarChatAi =
      document.getElementById(
        'btnSidebarChatAi'
      );


    [
      btnChatAi,
      btnSidebarChatAi
    ].forEach(
      btn => {

        if (btn) {

          btn.addEventListener(
            'click',
            (e) => {

              e.preventDefault();

              alert(
                'Chức năng "Chat với AI Assistant": Mở cửa sổ chatbot hỗ trợ thông minh.'
              );
            }
          );
        }

      }
    );


    // --------------------------------------------------------
    // MODAL CHI TIẾT TICKET
    // --------------------------------------------------------

    const btnModalClose =
      document.getElementById(
        'btnModalClose'
      );

    const ticketModal =
      document.getElementById(
        'ticketModal'
      );


    if (
      btnModalClose &&
      ticketModal
    ) {

      btnModalClose.addEventListener(
        'click',
        () => {

          ticketModal.classList.remove(
            'show'
          );
        }
      );


      ticketModal.addEventListener(
        'click',
        (e) => {

          if (
            e.target ===
            ticketModal
          ) {

            ticketModal.classList.remove(
              'show'
            );
          }
        }
      );
    }

  }
);


// ============================================================
// STATUS BADGE
// ============================================================

function getStatusBadge(status) {

  const normalizedStatus =
    status
      ? status.toLowerCase()
      : '';


  const map = {

    assigned: {

      label:
        'Chờ tiếp nhận',

      class:
        'badge-open'
    },

    open: {

      label:
        'Chờ tiếp nhận',

      class:
        'badge-open'
    },

    in_progress: {

      label:
        'Đang xử lý',

      class:
        'badge-in_progress'
    },

    resolved: {

      label:
        'Đã xử lý (Chờ nghiệm thu)',

      class:
        'badge-resolved'
    },

    closed: {

      label:
        'Đã đóng (Nghiệm thu xong)',

      class:
        'badge-closed'
    }

  };


  const item =
    map[normalizedStatus] || {

      label:
        status,

      class:
        'badge-closed'
    };


  return `
    <span class="ticket-badge ${item.class}">
      ${item.label}
    </span>
  `;
}


// ============================================================
// RENDER STATS - BACKEND
// ============================================================

function renderStatsFromBackend(ticketStats) {

  if (!ticketStats) {
    return;
  }


  const statOpen =
    document.getElementById(
      'statOpen'
    );

  const statProgress =
    document.getElementById(
      'statProgress'
    );

  const statResolved =
    document.getElementById(
      'statResolved'
    );

  const statClosed =
    document.getElementById(
      'statClosed'
    );


  if (statOpen) {

    statOpen.textContent =
      ticketStats.open ?? 0;
  }


  if (statProgress) {

    statProgress.textContent =
      ticketStats.in_progress ?? 0;
  }


  if (statResolved) {

    statResolved.textContent =
      ticketStats.resolved ?? 0;
  }


  if (statClosed) {

    statClosed.textContent =
      ticketStats.closed ?? 0;
  }
}


// ============================================================
// RENDER TICKETS TABLE - BACKEND
// ============================================================

function renderTicketsTableFromBackend(
  recentTickets
) {

  const tbody =
    document.getElementById(
      'ticketsTableBody'
    );


  if (!tbody) {
    return;
  }


  tbody.innerHTML = '';


  if (
    !recentTickets ||
    recentTickets.length === 0
  ) {

    const tr =
      document.createElement(
        'tr'
      );


    tr.innerHTML = `
      <td colspan="6" style="text-align: center;">
        Chưa có ticket nào.
      </td>
    `;


    tbody.appendChild(
      tr
    );

    return;
  }


  recentTickets.forEach(
    ticket => {

      const tr =
        document.createElement(
          'tr'
        );


      tr.className =
        'clickable-row';


      tr.innerHTML = `

        <td>
          <strong>#${ticket.id}</strong>
        </td>

        <td>
          ${ticket.title}
        </td>

        <td>
          ${ticket.category}
        </td>

        <td>
          ${getStatusBadge(ticket.status)}
        </td>

        <td>
          ${formatBackendDate(ticket.created_at)}
        </td>

        <td>
          <button
            class="btn-view-detail"
            data-id="${ticket.id}"
          >
            Chi tiết
          </button>
        </td>

      `;


      tr.addEventListener(
        'click',
        () => {

          openTicketDetail(
            ticket.id
          );
        }
      );


      tbody.appendChild(
        tr
      );

    }
  );
}


// ============================================================
// FORMAT BACKEND DATE
// ============================================================

function formatBackendDate(
  dateString
) {

  if (!dateString) {
    return '';
  }


  const date =
    new Date(
      dateString
    );


  if (
    Number.isNaN(
      date.getTime()
    )
  ) {

    return dateString;
  }


  return date.toLocaleString(
    'vi-VN',
    {
      dateStyle:
        'short',

      timeStyle:
        'short'
    }
  );
}


// ============================================================
// OPEN TICKET DETAIL
// PHASE 5 + PHASE 9
// ============================================================

async function openTicketDetail(ticketId) {

  try {

    // --------------------------------------------------------
    // GỌI BACKEND TICKET DETAIL
    // --------------------------------------------------------

    const response =
      await fetch(
        `http://127.0.0.1:5000/tickets/${ticketId}`,
        {
          method: 'GET',
          credentials: 'include'
        }
      );


    const result =
      await response.json();


    console.log(
      'Ticket Detail:',
      result
    );


    // --------------------------------------------------------
    // XỬ LÝ LỖI
    // --------------------------------------------------------

    if (
      !response.ok ||
      !result.success
    ) {

      if (response.status === 401) {

        alert(
          'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.'
        );

        window.location.href =
          '../login/login.html';

        return;
      }


      alert(
        result.error?.message ||
        'Không thể tải thông tin ticket.'
      );

      return;
    }


    // --------------------------------------------------------
    // LẤY DATA TỪ BACKEND
    // --------------------------------------------------------

    const ticket =
      result.data;


    const header =
      ticket.ticket_header;


    const info =
      ticket.ticket_info;


    const description =
      ticket.ticket_description;


    const history =
      ticket.ticket_history;


    // --------------------------------------------------------
    // TICKET HEADER
    // --------------------------------------------------------

    const modalPriority =
      document.getElementById(
        'modalTicketPriority'
      );

    const modalTitle =
      document.getElementById(
        'modalTicketTitle'
      );

    const modalId =
      document.getElementById(
        'modalTicketId'
      );


    if (modalPriority) {

      modalPriority.textContent =
        header.priority;
    }


    if (modalTitle) {

      modalTitle.textContent =
        header.title;
    }


    if (modalId) {

      modalId.textContent =
        header.id;
    }


    // --------------------------------------------------------
    // LOCATION
    // --------------------------------------------------------

    const modalLocation =
      document.getElementById(
        'modalLocation'
      );


    if (modalLocation) {

      const buildingName =
        info.location?.building?.name ||
        'Chưa xác định';


      const roomName =
        info.location?.room?.name ||
        'Chưa xác định';


      modalLocation.textContent =
        `${buildingName} - ${roomName}`;
    }


    // --------------------------------------------------------
    // CATEGORY
    // --------------------------------------------------------

    const modalCategory =
      document.getElementById(
        'modalCategory'
      );


    if (modalCategory) {

      modalCategory.textContent =
        info.category ||
        'Chưa xác định';
    }


    // --------------------------------------------------------
    // ASSIGNED TEAM
    // --------------------------------------------------------

    const modalAssignedTeam =
      document.getElementById(
        'modalAssignedTeam'
      );


    if (modalAssignedTeam) {

      modalAssignedTeam.textContent =
        info.assigned_team
          ? info.assigned_team.name
          : 'Chưa phân công';
    }


    // --------------------------------------------------------
    // ASSIGNED TECHNICIAN
    // --------------------------------------------------------

    const modalAssignedTech =
      document.getElementById(
        'modalAssignedTech'
      );


    if (modalAssignedTech) {

      modalAssignedTech.textContent =
        info.assigned_tech
          ? info.assigned_tech.name
          : 'Chưa có kỹ thuật viên';
    }


    // --------------------------------------------------------
    // DESCRIPTION
    // --------------------------------------------------------

    const modalDescription =
      document.getElementById(
        'modalDescription'
      );


    if (modalDescription) {

      modalDescription.textContent =
        description.description ||
        'Không có mô tả.';
    }


    // --------------------------------------------------------
    // TICKET HISTORY
    // --------------------------------------------------------

    const timeline =
      document.getElementById(
        'modalTimeline'
      );


    if (timeline) {

      timeline.innerHTML = '';


      if (
        !history ||
        history.length === 0
      ) {

        timeline.innerHTML = `
          <div class="timeline-item">
            <div class="timeline-content">
              Chưa có lịch sử xử lý.
            </div>
          </div>
        `;

      } else {

        history.forEach(
          item => {

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
              '—';


            const time =
              item.time
                ? new Date(
                    item.time
                  ).toLocaleString(
                    'vi-VN'
                  )
                : '—';


            timeline.innerHTML += `
              <div class="timeline-item">

                <div class="timeline-content">

                  <div>
                    <strong>
                      ${oldStatus}
                    </strong>

                    →

                    <strong>
                      ${newStatus}
                    </strong>
                  </div>

                  <div>
                    ${note}
                  </div>

                  <small>
                    ${time} · ${updatedBy}
                  </small>

                </div>

              </div>
            `;
          }
        );
      }
    }


    // ========================================================
    // FOOTER ACTIONS
    // PHASE 9 - CLOSE / REOPEN
    // ========================================================

    const footer =
      document.getElementById(
        'modalFooterActions'
      );


    if (footer) {

      // Xóa các nút cũ trước khi render
      footer.innerHTML = '';


      const status =
        String(
          header.status || ''
        ).toLowerCase();


      // ------------------------------------------------------
      // RESOLVED
      // ------------------------------------------------------
      // User có 2 lựa chọn:
      //
      // 1. Xác nhận hoàn tất
      //    RESOLVED -> CLOSED
      //
      // 2. Yêu cầu xử lý tiếp
      //    RESOLVED -> IN_PROGRESS
      // ------------------------------------------------------

      if (status === 'resolved') {

        footer.innerHTML = `

          <button
            type="button"
            class="btn btn-primary"
            id="btnConfirmComplete"
          >
            Xác nhận hoàn tất
          </button>

          <button
            type="button"
            class="btn btn-secondary"
            id="btnRequestReopen"
          >
            Yêu cầu xử lý tiếp
          </button>

        `;


        // ----------------------------------------------------
        // XÁC NHẬN HOÀN TẤT
        // ----------------------------------------------------

        const btnConfirmComplete =
          document.getElementById(
            'btnConfirmComplete'
          );


        if (btnConfirmComplete) {

          btnConfirmComplete.addEventListener(
            'click',
            () => {

              closeTicket(
                header.id
              );

            }
          );
        }


        // ----------------------------------------------------
        // YÊU CẦU XỬ LÝ TIẾP
        // ----------------------------------------------------

        const btnRequestReopen =
          document.getElementById(
            'btnRequestReopen'
          );


        if (btnRequestReopen) {

          btnRequestReopen.addEventListener(
            'click',
            () => {

              reopenTicket(
                header.id
              );

            }
          );
        }

      }

    }


    // --------------------------------------------------------
    // HIỂN THỊ MODAL
    // --------------------------------------------------------

    const ticketModal =
      document.getElementById(
        'ticketModal'
      );


    if (ticketModal) {

      ticketModal.classList.add(
        'show'
      );
    }

  } catch (error) {

    console.error(
      'Lỗi khi tải Ticket Detail:',
      error
    );


    alert(
      'Không thể kết nối đến Backend. Vui lòng kiểm tra server.'
    );
  }
}


// ============================================================
// CLOSE TICKET
// PHASE 9 - USER XÁC NHẬN HOÀN TẤT
// RESOLVED -> CLOSED
// ============================================================

async function closeTicket(ticketId) {

  if (!ticketId) {

    alert(
      'Không xác định được Ticket.'
    );

    return;
  }


  const confirmed =
    confirm(
      'Bạn xác nhận sự cố đã được xử lý hoàn tất?'
    );


  if (!confirmed) {
    return;
  }


  try {

    const response =
      await fetch(
        `http://127.0.0.1:5000/tickets/${ticketId}/close`,
        {
          method: 'POST',
          credentials: 'include'
        }
      );


    const result =
      await response.json();


    // --------------------------------------------------------
    // SESSION HẾT HẠN
    // --------------------------------------------------------

    if (response.status === 401) {

      alert(
        'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.'
      );

      window.location.href =
        '../login/login.html';

      return;
    }


    // --------------------------------------------------------
    // BACKEND ERROR
    // --------------------------------------------------------

    if (
      !response.ok ||
      !result.success
    ) {

      alert(
        result.error?.message ||
        'Không thể xác nhận hoàn tất ticket.'
      );

      return;
    }


    // --------------------------------------------------------
    // SUCCESS
    // --------------------------------------------------------

    alert(
      `Đã xác nhận hoàn tất ticket #${ticketId}.`
    );


    // Cập nhật Dashboard
    await loadDashboardData();


    // Cập nhật lại Ticket Detail
    await openTicketDetail(
      ticketId
    );

  } catch (error) {

    console.error(
      'Close ticket error:',
      error
    );


    alert(
      'Không thể kết nối đến Backend.'
    );
  }
}


// ============================================================
// REOPEN TICKET
// PHASE 9 - USER YÊU CẦU XỬ LÝ TIẾP
// RESOLVED -> IN_PROGRESS
// ============================================================

async function reopenTicket(ticketId) {

  if (!ticketId) {

    alert(
      'Không xác định được Ticket.'
    );

    return;
  }

  const reason =
    prompt(
      'Vui lòng nhập lý do yêu cầu xử lý tiếp:'
    );


  if (reason === null) {
    return;
  }


  const trimmedReason =
    reason.trim();


  if (!trimmedReason) {

    alert(
      'Vui lòng nhập lý do yêu cầu xử lý tiếp.'
    );

    return;
  }


  try {

    const response =
      await fetch(
        `http://127.0.0.1:5000/tickets/${ticketId}/reopen`,
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json'
          },

          credentials: 'include',

          body:
            JSON.stringify({
              note:
                trimmedReason
            })
        }
      );


    const result =
      await response.json();


    // --------------------------------------------------------
    // SESSION HẾT HẠN
    // --------------------------------------------------------

    if (response.status === 401) {

      alert(
        'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.'
      );

      window.location.href =
        '../login/login.html';

      return;
    }


    // --------------------------------------------------------
    // BACKEND ERROR
    // --------------------------------------------------------

    if (
      !response.ok ||
      !result.success
    ) {

      alert(
        result.error?.message ||
        'Không thể yêu cầu xử lý tiếp.'
      );

      return;
    }


    // --------------------------------------------------------
    // SUCCESS
    // --------------------------------------------------------

    alert(
      `Đã gửi yêu cầu xử lý tiếp cho ticket #${ticketId}.`
    );


    // Cập nhật Dashboard
    await loadDashboardData();


    // Cập nhật lại Ticket Detail
    await openTicketDetail(
      ticketId
    );

  } catch (error) {

    console.error(
      'Reopen ticket error:',
      error
    );


    alert(
      'Không thể kết nối đến Backend.'
    );
  }
}