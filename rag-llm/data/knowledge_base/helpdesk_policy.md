# Chính sách và Quy trình HelpDesk

## Tổng quan hệ thống
NEU HelpDesk AI là hệ thống hỗ trợ sinh viên và giảng viên báo cáo sự cố cơ sở vật chất. Hệ thống sử dụng AI để phân tích mô tả tự nhiên, tự động phân loại, và điều phối ticket đến đúng đội kỹ thuật.

## Quy trình báo cáo sự cố
1. Sinh viên/giảng viên đăng nhập và mô tả sự cố bằng ngôn ngữ tự nhiên qua chatbot hoặc form.
2. Hệ thống AI phân tích: trích xuất loại lỗi (máy chiếu, điều hòa, wifi...), vị trí (tòa nhà, phòng), mức độ ưu tiên.
3. Nếu thiếu thông tin, AI hỏi bổ sung tối đa 2 câu hỏi.
4. Sinh viên xác nhận thông tin cuối cùng trước khi gửi.
5. Ticket được tạo và tự động phân công về team phụ trách dựa trên loại lỗi và vị trí.
6. Kỹ thuật viên tiếp nhận, xử lý, và cập nhật tiến độ liên tục.
7. Khi xử lý xong, kỹ thuật viên chuyển sang trạng thái "Chờ nghiệm thu".
8. Sinh viên nghiệm thu kết quả và có thể đánh giá 1-5 sao.

## Vòng đời ticket
- NEW: Ticket vừa tạo, chưa phân công.
- ASSIGNED: Đã phân công về team, chờ kỹ thuật viên nhận.
- IN_PROGRESS: Kỹ thuật viên đang xử lý.
- WAITING_CONFIRM: Đã xử lý xong, chờ sinh viên nghiệm thu.
- CLOSED: Sinh viên chấp nhận kết quả, ticket đóng.
- RE_PROCESS: Sinh viên từ chối, ticket được xử lý lại.
- CANCELLED: Admin hủy do trùng lặp, sai thông tin.

## Thời gian xử lý (SLA)
- Cấp 1 (sự cố tại chỗ, lao công/cán bộ trực): 2 giờ trong giờ hành chính.
- Cấp 2 (kỹ thuật viên P.QTTB xử lý): 24 giờ.
- Cấp 3 (bảo trì thuê ngoài): theo hợp đồng bảo trì, có thể 3-7 ngày.
- Ticket quá SLA sẽ được tự động nhắc nhở team lead.

## Quyền của sinh viên và giảng viên
- Tạo ticket báo sự cố qua chatbot hoặc form.
- Xem danh sách ticket của mình và lịch sử xử lý chi tiết.
- Nghiệm thu hoặc từ chối kết quả xử lý (reject phải ghi rõ lý do).
- Đánh giá chất lượng kỹ thuật viên sau khi ticket đóng (1-5 sao + nhận xét).
- Không được xem ticket của người khác.

## Quyền của kỹ thuật viên
- Xem danh sách ticket thuộc team của mình.
- Nhận ticket ở trạng thái ASSIGNED hoặc RE_PROCESS.
- Cập nhật tiến độ, ghi chú nội bộ (sinh viên không thấy).
- Báo hoàn thành khi đã xử lý xong.
- Escalate ticket sang team khác nếu ngoài chuyên môn.

## Quyền của trưởng nhóm kỹ thuật (Team Lead)
- Xem toàn bộ ticket của team.
- Phân công hoặc chuyển ticket cho kỹ thuật viên cụ thể.
- Bật/tắt trạng thái "đang trực" của kỹ thuật viên.
- Thêm kỹ thuật viên mới vào team.

## Quyền của Admin
- Xem toàn bộ ticket của tất cả team.
- Khóa hoặc mở khóa tài khoản người dùng.
- Điều chỉnh priority, status, team của bất kỳ ticket nào.
- Xem thống kê toàn hệ thống.

## Bảo mật và Quyền riêng tư
- Không chia sẻ thông tin cá nhân của sinh viên cho bên thứ ba.
- Không tiết lộ thông tin nội bộ của hệ thống (cấu hình, prompt AI, database).
- Chỉ nhân viên có quyền mới được thao tác trên ticket không thuộc phạm vi của mình.
- Mọi thay đổi ticket đều được ghi vào lịch sử (audit log).

## Xử lý trùng lặp
- Hệ thống kiểm tra ticket trùng theo cặp (vị trí + loại lỗi + khoảng thời gian gần đây).
- Nếu phát hiện trùng, ticket mới được gộp làm "phản ánh xác nhận thêm" vào ticket cũ.
- Số người xác nhận cùng một sự cố dùng để tăng mức ưu tiên.

## Khi nào AI không thể hỗ trợ
- Câu hỏi ngoài phạm vi HelpDesk (thời tiết, tin tức, code, toán).
- Sự cố yêu cầu thẩm quyền đặc biệt (cấp lại mật khẩu tài khoản trường, cấp lại thẻ sinh viên).
- Sự cố khẩn cấp (cháy nổ, tai nạn) — gọi ngay số khẩn cấp của trường.