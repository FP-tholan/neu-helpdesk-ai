
## 1. Business Workflow (Quy trình Hoạt động Tổng thể)

| Stt | Chặng | Tên bước |                Giải thích |
| :---: | :--- | :--- | :--- |
| **1** | **Bắt đầu (input)** | `Student / Lecturer` ➔ `Chatbot` | Người dùng nhập thông tin đầu vào cho Chatbot tiếp nhận. |
| **2.1** | **Phân luồng (Router)** | `Router` ➔ `RAG` |  Hỏi đáp / Tra cứu ➔ Xuất ra hướng dẫn (FAQ / Troubleshooting) cho người dùng tự khắc phục. |
| **2.2** | **Phân luồng (Router)** | `Router` ➔ `Agent` |  Sự cố thật sự cần thợ ➔ Chuyển sang xử lý Ticket-related processing để tạo đơn. |
| **3** | **Khởi tạo (Backend)** | `Backend` ➔ `Ticket` ➔ `Responsible Team` | Máy lưu bản ghi Ticket và chạy luật gán về đúng Đội kỹ thuật phụ trách. |
| **4** | **Thi công** | `Technician` ➔ `Update Ticket` | Thợ nhận đơn, đến hiện trường sửa chữa và bấm cập nhật trạng thái "Đã xong". |
| **5.1** | **Nghiệm thu** | `Student` ➔ `Accept` ➔ `Closed` | **Trường hợp 1:** Sinh viên đồng ý kết quả ➔ Đóng Ticket hoàn tất. |
| **5.2** | **Nghiệm thu** | `Student` ➔ `Reject` ➔ `Re-process` | **Trường hợp 2** Sinh viên không đồng ý ➔ Đẩy Ticket về làm lại. |




##


---

## 2. Ticket Lifecycle (Vòng đời và Trạng thái Ticket)

| Stt | Trạng thái (Status Code) | Tên hiển thị | Đối tượng kích hoạt (Actor) | Giải thích & Điều kiện chuyển trạng thái |
| :---: | :--- | :--- | :--- | :--- |
| **1** | `NEW` | Mới tạo | Chatbot / Backend | Ticket vừa được khởi tạo thành công từ hội thoại AI, chờ phân công. |
| **2** | `ASSIGNED` | Đã phân công | Dispatch Engine | Hệ thống tự động phân loại và gán Ticket cho Đội kỹ thuật phụ trách. |
| **3** | `IN_PROGRESS` | Đang xử lý | Kỹ thuật viên (Technician) | Kỹ thuật viên nhấn nhận đơn và bắt đầu sửa chữa tại hiện trường. |
| **4** | `WAITING_CONFIRM` | Chờ nghiệm thu | Kỹ thuật viên (Technician) | Thợ hoàn thành công việc và gửi yêu cầu nghiệm thu đến người dùng. |
| **5.1** | `CLOSED` | Đã đóng | Sinh viên / Giảng viên | **Trường hợp Accept:** Người dùng xác nhận thiết bị đã sử dụng bình thường. |
| **5.2** | `CLOSED` | Đã đóng (Tự động) | Hệ thống (System) | **Trường hợp Timeout:** Tự động đóng đơn sau 48h nếu người dùng không phản hồi. |
| **6** | `RE_PROCESS` | Cần xử lý lại | Sinh viên / Giảng viên | **Trường hợp Reject:** Người dùng từ chối nghiệm thu, ticket đẩy lại kỹ thuật viên. |
| **7** | `CANCELLED` | Đã hủy | Admin / System | Ticket bị hủy do khai báo sai, thông tin ảo hoặc trùng lặp. 






---

## 
##

##
##
## 3. Dispatch (Cơ chế Phân công Tự động)
| Stt | Tiêu chí Vị trí (Location) | Tiêu chí Sự cố (Category) | Đội phụ trách (Responsible Team) | Giải thích & Quy tắc Phân công |
| :---: | :--- | :--- | :--- | :--- |
| **1** | Toàn trường (All Buildings) | IT / Network / Software | **Team IT** (`T_IT`) | Các sự cố liên quan đến Mạng Wifi, Máy tính phòng Lab, Phần mềm, Tài khoản hệ thống. |
| **2** | Tòa A1, A2 | Infrastructure / Electricity | **Team PSA** (`T_PSA`) | Sự cố cơ sở vật chất, điện, nước, điều hòa, bàn ghế tại các tòa hành chính A1, A2. |
| **3** | Tòa B, C, D | Infrastructure / Equipment | **Team QTTB** (`T_QTTB`) | Sự cố cơ sở vật chất, máy chiếu, âm thanh, điều hòa tại các tòa giảng đường B, C, D (Ví dụ: B203). |
| **4** | Không xác định / Khác | General / Unmapped | **Helpdesk Admin** | Sự cố không khớp với quy tắc tự động sẽ chuyển về hàng chờ Admin phân công thủ công. 

---

## 4. Permission (Phân quyền Hệ thống)

| Stt | Vai trò (Role) | Mã vai trò (Role Code) | Quyền hạn & Phạm vi Xử lý |
| :---: | :--- | :--- | :--- |
| **1** | Sinh viên / Giảng viên | `USER` | Tạo đơn báo hỏng qua Chatbot, theo dõi trạng thái, nghiệm thu (Accept/Reject) đơn của chính mình. |
| **2** | Kỹ thuật viên | `TECHNICIAN` | Xem danh sách đơn được gán cho Đội, nhận đơn (`IN_PROGRESS`), cập nhật tiến độ và báo hoàn thành (`WAITING_CONFIRM`). |
| **3** | Trưởng đội kỹ thuật | `TEAM_LEAD` | Giám sát toàn bộ đơn của Đội phụ trách, can thiệp xử lý đơn `RE_PROCESS`, gán/chuyển đơn thủ công cho KTV. |
| **4** | Quản trị viên Hệ thống | `ADMIN` | Độc quyền xem toàn bộ đơn hệ thống, cấu hình luật Dispatch, quản lý tài khoản người dùng và hủy đơn (`CANCELLED`). 



|






------

## 5. Escalation (Quy tắc Leo thang)

| Stt | Mã Quy tắc | Điều kiện kích hoạt | Bước | Hành động của Hệ thống |
| :---: | :--- | :--- | :---: | :--- |
| **1** | `ESC_REPROCESS` | Người dùng chọn `Reject` khi nghiệm thu | 1 | Đổi trạng thái Ticket sang `RE_PROCESS`. |
| | | | 2 | Tự động nâng mức ưu tiên (`Priority`) lên `HIGH`. |
| | | | 3 | Bắn thông báo trực tiếp tới Trưởng đội (`TEAM_LEAD`). |
| **2** | `ESC_SLA_ACCEPT` | Ticket ở trạng thái `ASSIGNED` quá 2h chưa KTV nào nhận | 1 | Gửi thông báo nhắc nhở tới toàn bộ KTV trong Đội. |
| | | | 2 | Ghi nhận cảnh báo trễ hạn trên Dashboard của `TEAM_LEAD`. |
| **3** | `ESC_SLA_FIX` | Ticket ở trạng thái `IN_PROGRESS` quá 24h chưa xong | 1 | Tự động gắn nhãn `OVERDUE` (Quá hạn SLA). |
| | | | 2 | Gửi thông báo yêu cầu `TEAM_LEAD` can thiệp kiểm tra. |

---

## 6. Business Rules (Ràng buộc Nghiệp vụ)
| Stt | Mã Luật | Tên Luật Nghiệp vụ | Chi tiết Logic & Ràng buộc |
| :---: | :--- | :--- | :--- |
| **1** | `BR_AUTO_CLOSE` | Tự động nghiệm thu | Tự động chuyển Ticket sang `CLOSED` sau 48 giờ ở trạng thái `WAITING_CONFIRM` nếu người dùng không phản hồi. |
| **2** | `BR_ANTI_SPAM` | Chống trùng lặp đơn | Tự động chuyển Ticket mới sang `CANCELLED` nếu đã có đơn cùng `Location` và `Category` đang trong quá trình xử lý. |
| **3** | `BR_MANDATORY_INFO` | Thông tin bắt buộc | Agent bắt buộc phải thu thập đủ 3 trường `Location`, `Category`, và `Description` trước khi tạo Ticket. |


## 
