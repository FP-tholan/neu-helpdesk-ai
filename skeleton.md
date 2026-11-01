# SKELETON BÁO CÁO PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG NEU HELPDESK AI

## Phần đầu báo cáo

1. Trang bìa
2. Mục lục
3. Danh mục hình vẽ
4. Danh mục bảng biểu
5. Danh mục từ viết tắt

# Chương 1. Tổng quan về đề tài

### 1.1. Bối cảnh và lý do lựa chọn đề tài

- Thực trạng tiếp nhận và xử lý sự cố trong môi trường đại học.
- Những bất tiện khi người dùng phản ánh sự cố qua các kênh riêng lẻ.
- Nhu cầu xây dựng hệ thống hỗ trợ tiếp nhận, phân loại và quản lý sự cố tập trung.
- Vai trò của AI trong việc hỗ trợ người dùng mô tả và phân loại sự cố.

### 1.2. Mục tiêu của hệ thống

- Tập trung hóa quy trình tiếp nhận phản ánh.
- Hỗ trợ phân loại sự cố bằng AI.
- Tự động điều phối sự cố đến bộ phận phù hợp.
- Theo dõi tiến độ và thời gian xử lý.
- Hỗ trợ nghiệm thu và đánh giá kết quả xử lý.
- Lưu trữ dữ liệu phục vụ thống kê, báo cáo.

### 1.3. Đối tượng và phạm vi nghiên cứu

- Đối tượng sử dụng: Sinh viên, giảng viên, nhân viên kỹ thuật, trưởng đội, quản trị viên.
- Đơn vị nghiệp vụ liên quan: Phòng Quản trị thiết bị (P.QTTB).
- Phạm vi chức năng của hệ thống.
- Những nội dung nằm ngoài phạm vi triển khai hiện tại.

### 1.4. Phương pháp thực hiện

- Khảo sát và phân tích quy trình nghiệp vụ.
- Xác định yêu cầu chức năng và phi chức năng.
- Mô hình hóa bằng UML.
- Thiết kế dữ liệu và kiến trúc hệ thống.

### 1.5. Công nghệ và công cụ dự kiến

- Frontend, Backend, Database.
- AI/LLM, RAG.
- Công cụ thiết kế UML và phát triển hệ thống.

# Chương 2. Khảo sát và phân tích nghiệp vụ

Đây là chương quan trọng, cần làm rõ hệ thống giải quyết vấn đề gì và quy trình nghiệp vụ sau khi áp dụng hệ thống sẽ vận hành như thế nào.

### 2.1. Khảo sát quy trình hiện tại (As-Is)

- Các kênh tiếp nhận phản ánh hiện tại.
- Cách thức ghi nhận thông tin sự cố.
- Quy trình phân công nhân sự xử lý.
- Cách theo dõi tiến độ và nghiệm thu.
- Những khó khăn, hạn chế của quy trình hiện tại.

Lưu ý: Những thông tin chưa khảo sát được thực tế tại NEU cần ghi rõ là nội dung cần xác minh, không tự đưa ra số liệu hoặc kết luận về quy trình hiện tại.

### 2.2. Quy trình nghiệp vụ đề xuất (To-Be)

Mô tả quy trình xử lý phản ánh NEU HelpDesk AI theo 10 bước:

| Bước | Nội dung nghiệp vụ                               |
| ---- | ------------------------------------------------ |
| 1    | Người dùng gửi phản ánh sự cố                    |
| 2    | AI phân tích và tự động điền thông tin           |
| 3    | Kiểm tra khả năng tự xử lý Cấp 0                 |
| 4    | AI hỏi bổ sung thông tin còn thiếu               |
| 5    | Kiểm tra phản ánh trùng lặp                      |
| 6    | Người dùng xác nhận và tạo Ticket                |
| 7    | Tự động điều phối sự cố theo cấp                 |
| 8    | Theo dõi tiến độ và giám sát SLA                 |
| 9    | Người dùng nghiệm thu, yêu cầu xử lý lại nếu cần |
| 10   | Đóng Ticket và lưu trữ dữ liệu                   |

Sau bảng tổng quan, trình bày chi tiết từng bước: tác nhân tham gia, dữ liệu đầu vào, hoạt động xử lý, kết quả đầu ra và điều kiện chuyển sang bước tiếp theo.

### 2.3. Các quy tắc nghiệp vụ

Tổng hợp thành các quy tắc có mã định danh để dễ đối chiếu với thiết kế hệ thống.

Ví dụ:

- BR01 – Thông tin vị trí sự cố phải được xác định trước khi tạo Ticket.
- BR02 – AI chỉ được đề xuất hướng dẫn tự xử lý khi sự cố thuộc danh mục được P.QTTB phê duyệt.
- BR03 – Phản ánh trùng lặp được liên kết với Ticket đang mở thay vì tạo Ticket mới.
- BR04 – Ticket được điều phối đến cấp xử lý phù hợp.
- BR05 – Việc chuyển từ Cấp 2 lên Cấp 3 cần P.QTTB phê duyệt.
- BR06 – Ticket chỉ được đóng khi người dùng xác nhận sự cố đã được xử lý.
- BR07 – Nếu người dùng không nghiệm thu, Ticket được chuyển sang cấp xử lý tiếp theo.

### 2.4. Các vấn đề cần thống nhất với đơn vị nghiệp vụ

- Danh mục sự cố được phép tự xử lý.
- Ngưỡng confidence của AI.
- Khoảng thời gian và ngưỡng tương đồng để phát hiện trùng lặp.
- Thời gian SLA của từng cấp.
- Quy trình xử lý khi Cấp 3 vẫn không khắc phục được sự cố.

# Chương 3. Phân tích yêu cầu và mô hình hóa chức năng

Chương này tập trung trả lời: Hệ thống có những chức năng gì, ai sử dụng và các chức năng liên hệ với nhau như thế nào?

### 3.1. Xác định tác nhân của hệ thống

| Tác nhân     | Vai trò                                               |
| ------------ | ----------------------------------------------------- |
| USER         | Sinh viên, giảng viên gửi phản ánh và theo dõi Ticket |
| TECHNICIAN   | Nhân viên kỹ thuật tiếp nhận và xử lý sự cố           |
| TEAM_LEAD    | Trưởng đội quản lý, phân công và giám sát             |
| ADMIN        | Quản lý tài khoản và cấu hình hệ thống                |
| AI Assistant | Hỗ trợ tiếp nhận, phân tích và trả lời người dùng     |

### 3.2. Xác định yêu cầu chức năng

Chia theo nhóm chức năng:

- FR01 – Quản lý tài khoản và xác thực.
- FR02 – Tiếp nhận và quản lý phản ánh.
- FR03 – Phân loại sự cố bằng AI.
- FR04 – Hướng dẫn tự xử lý.
- FR05 – Phát hiện phản ánh trùng lặp.
- FR06 – Điều phối và phân công Ticket.
- FR07 – Xử lý và cập nhật trạng thái Ticket.
- FR08 – Theo dõi SLA và cảnh báo quá hạn.
- FR09 – Nghiệm thu và chuyển cấp xử lý.
- FR10 – Thống kê và báo cáo.
- FR11 – Hỏi đáp và truy xuất tri thức bằng AI/RAG.

### 3.3. Xác định yêu cầu phi chức năng

- Hiệu năng.
- Bảo mật và phân quyền.
- Tính sẵn sàng.
- Khả năng mở rộng.
- Khả năng bảo trì.
- Khả năng sử dụng.
- Độ tin cậy của kết quả AI.

### 3.4. Biểu đồ Use Case tổng quan – A1

- Mục đích biểu đồ.
- Các tác nhân.
- Các nhóm chức năng chính.
- Quan hệ giữa tác nhân và hệ thống.

### 3.5. Biểu đồ Use Case phân rã – A2

Phân rã thành các nhóm:

- User
- Technician
- Team_lead
- Admin

# Chương 4. Phân tích quy trình và tương tác hệ thống

Chương 3 mô tả hệ thống có chức năng gì. Chương 4 đi sâu vào các chức năng được thực hiện theo trình tự nào và các thành phần tương tác ra sao.

### 4.1. Mô hình hóa quy trình nghiệp vụ bằng Activity Diagram

- B1. Biểu đồ hoạt động tiếp nhận và tạo Ticket.
- B2. Biểu đồ hoạt động xử lý và nghiệm thu Ticket.
- B3. Biểu đồ hoạt động tự động điều phối Ticket.
- B4. Biểu đồ hoạt động quản lý tài khoản và đặt lại mật khẩu.
- B5. Biểu đồ hoạt động giám sát SLA và xử lý Ticket quá hạn.

Với mỗi biểu đồ:

- Mục đích.
- Tác nhân tham gia.
- Diễn giải các luồng hoạt động.
- Các nhánh điều kiện quan trọng.

### 4.2. Mô hình hóa tương tác bằng Sequence Diagram

- C1. Biểu đồ tuần tự tạo Ticket.
- C2. Biểu đồ tuần tự điều phối Ticket.
- C3. Biểu đồ tuần tự xử lý và nghiệm thu Ticket.
- C4. Biểu đồ tuần tự đặt lại mật khẩu.
- C5. Biểu đồ tuần tự truy xuất Dashboard và KPI.
- C6. Biểu đồ tuần tự chatbot AI/RAG.

Với mỗi biểu đồ:

- Các đối tượng tham gia.
- Trình tự gửi và nhận thông điệp.
- Vai trò của Frontend, Backend, Service và Database.
- Các nhánh xử lý thay thế nếu có.

# Chương 5. Thiết kế dữ liệu và kiến trúc hệ thống

Mình đề xuất gộp thiết kế dữ liệu và kiến trúc vào cùng một chương vì đây đều là phần thiết kế kỹ thuật, nhưng chia thành hai mục lớn để không bị lẫn.

### 5.1. Thiết kế dữ liệu

#### 5.1.1. Biểu đồ lớp chi tiết – D1

Trình bày các lớp chính:

- User.
- Ticket.
- Team.
- Building.
- Room.
- TicketHistory.
- DispatchRule.

Giải thích:

- Thuộc tính và kiểu dữ liệu.
- Phương thức chính.
- Quan hệ giữa các lớp.
- Bội số quan hệ (Multiplicity).

#### 5.1.2. Mô tả các thực thể dữ liệu

Mô tả mục đích và vai trò của từng thực thể trong hệ thống.

#### 5.1.3. Thiết kế cơ sở dữ liệu quan hệ

- Danh sách các bảng.
- Khóa chính, khóa ngoại.
- Quan hệ giữa các bảng.
- Các ràng buộc dữ liệu quan trọng.

### 5.2. Thiết kế kiến trúc hệ thống

#### 5.2.1. Biểu đồ gói – E1

Mô tả các package:

- Frontend.
- Authentication.
- Ticket Management.
- Dispatch Management.
- User Management.
- Reporting & SLA.
- Data Access.
- AI/RAG.

#### 5.2.2. Biểu đồ thành phần – E2

- Các thành phần chính.
- Quan hệ phụ thuộc.
- Giao tiếp giữa Frontend, Backend, Database và AI Service.

#### 5.2.3. Biểu đồ triển khai – E3

- Môi trường triển khai hiện tại.
- Các node phần cứng/phần mềm.
- Cách các thành phần được triển khai và kết nối.
- Phân biệt môi trường demo và kiến trúc triển khai mục tiêu.

### 5.3. Thiết kế kiến trúc AI/RAG

#### 5.3.1. Biểu đồ thành phần AI/RAG – F1

Mô tả vai trò:

- Router.
- Agent.
- Retriever.
- Reranker.
- LLM.
- Memory.
- Knowledge Base.

#### 5.3.2. Biểu đồ hoạt động chatbot tiếp nhận sự cố – F2

Mô tả luồng:

- Người dùng gửi nội dung.
- AI xác định Intent.
- Phân tích thông tin.
- Hỏi bổ sung nếu thiếu.
- Đưa ra hướng dẫn tự xử lý hoặc đề xuất tạo Ticket.

#### 5.3.3. Biểu đồ tuần tự truy vấn tri thức – F3

Mô tả quá trình:

- Người dùng gửi câu hỏi.
- Backend chuyển yêu cầu đến Router.
- Retriever truy xuất tài liệu.
- Reranker sắp xếp kết quả.
- LLM tạo câu trả lời dựa trên ngữ cảnh.
- Trả kết quả về Frontend.

# Chương 6. Thiết kế giao diện và kết luận

### 6.1. Thiết kế giao diện người dùng

#### 6.1.1. Giao diện dành cho người phản ánh

- Trang gửi phản ánh.
- Giao diện chatbot hỗ trợ nhập thông tin.
- Giao diện xác nhận thông tin Ticket.
- Giao diện hướng dẫn tự xử lý.
- Trang theo dõi trạng thái Ticket.
- Giao diện nghiệm thu kết quả.

#### 6.1.2. Giao diện dành cho nhân viên kỹ thuật

- Dashboard công việc.
- Danh sách Ticket được giao.
- Chi tiết Ticket.
- Giao diện cập nhật tiến độ xử lý.

#### 6.1.3. Giao diện dành cho trưởng đội và P.QTTB

- Dashboard tổng quan.
- Quản lý và điều phối Ticket.
- Phê duyệt chuyển cấp xử lý.
- Theo dõi SLA.
- Báo cáo thống kê.

#### 6.1.4. Giao diện quản trị viên

- Quản lý tài khoản.
- Phân quyền.
- Quản lý cấu hình hệ thống.

### 6.2. Đánh giá phạm vi triển khai

Phân biệt rõ:

- Các chức năng đã triển khai trong phiên bản demo.
- Các chức năng mới ở mức thiết kế hoặc định hướng phát triển.
- Những chức năng cần tích hợp thêm với hệ thống của nhà trường.

### 6.3. Kết luận và hướng phát triển

- Tổng kết kết quả phân tích và thiết kế.
- Những hạn chế còn tồn tại.
- Hướng phát triển tiếp theo.

# Phụ lục

Không cần đưa quá nhiều nội dung vào chương chính. Có thể chuyển các phần mang tính tra cứu xuống phụ lục:

- Phụ lục A: Danh mục yêu cầu chức năng và phi chức năng.
- Phụ lục B: Danh mục quy tắc nghiệp vụ BR.
- Phụ lục C: Bảng mô tả chi tiết các trường dữ liệu.
- Phụ lục D: Bảng đối chiếu yêu cầu – Use Case – biểu đồ – dữ liệu.
- Phụ lục E: Phiếu khảo sát quy trình hiện tại.
- Phụ lục F: Các biểu đồ UML kích thước lớn (nếu không tiện đặt trong chương).

## Những phần đã được gộp và lý do

| Cấu trúc cũ         | Cấu trúc mới | Lý do                                   |
| ------------------- | ------------ | --------------------------------------- |
| Tổng quan đề tài    | Chương 1     | Giữ nguyên                              |
| Khảo sát hiện trạng | Chương 2     | Gộp phân tích As-Is và To-Be            |
| Phân tích yêu cầu   | Chương 3     | Đặt Use Case cùng yêu cầu hệ thống      |
| Activity + Sequence | Chương 4     | Cùng mô tả quy trình và tương tác       |
| Thiết kế dữ liệu    | Chương 5.1   | Gộp với kiến trúc hệ thống              |
| Kiến trúc hệ thống  | Chương 5.2   | Gồm E1, E2, E3                          |
| Thiết kế AI/RAG     | Chương 5.3   | Đặt cùng kiến trúc kỹ thuật             |
| Thiết kế giao diện  | Chương 6.1   | Giữ riêng vì là phần thiết kế trực quan |
| Kết luận            | Chương 6.3   | Gộp với đánh giá triển khai             |

