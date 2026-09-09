# Tài liệu nghiệp vụ — Phạm vi bản Demo NEU HelpDesk AI

## 1. Mục đích tài liệu

Tài liệu này xác định rõ ranh giới giữa **hệ thống được đề xuất trong đặc tả nghiệp vụ đầy đủ** và **bản demo minh họa** phục vụ báo cáo môn Quản lý dự án. Mục tiêu là chứng minh tính khả thi của ý tưởng và năng lực triển khai kỹ thuật của nhóm, không phải xây dựng sản phẩm hoàn chỉnh sẵn sàng vận hành.

## 2. Kịch bản demo được chọn

**Tình huống minh họa:** "Máy chiếu phòng A302 không hoạt động trong giờ học."

Lý do chọn kịch bản này:
- Đi xuyên suốt được toàn bộ vòng đời một ticket: nhập → AI phân tích → dispatch → theo dõi → nghiệm thu.
- Là lỗi mức trung bình (không thuộc diện tự xử lý Cấp 0, không phải hỏng nặng cần Cấp 3), nên thể hiện được rõ nhất cơ chế auto-dispatch — phần lõi kỹ thuật của đề án.

## 3. Phạm vi triển khai (In scope)

| Hạng mục | Mô tả | Cách triển khai trong demo |
|---|---|---|
| Nhập phản ánh | Sinh viên nhập mô tả bằng ngôn ngữ tự nhiên | Form nhập liệu web, có chọn phòng từ danh sách dựng sẵn |
| AI phân tích & phân loại | Trích xuất loại lỗi, vị trí, mức ưu tiên từ mô tả | Gọi API LLM thật (OpenAI/Gemini/Anthropic), trả về kết quả dạng JSON hiển thị trực tiếp trên giao diện |
| Auto-dispatch | Định tuyến ticket đến đúng cấp xử lý | Logic if/else dựa trên nhãn AI trả về, ánh xạ tới 3 cấp (giảng đường / P.QTTB / bảo trì ngoài) |
| Theo dõi trạng thái | Xem tiến độ xử lý ticket theo thời gian thực | Dashboard đơn giản, cập nhật trạng thái qua thao tác thủ công của tài khoản demo đóng vai cán bộ xử lý |
| Nghiệm thu & escalate | Sinh viên xác nhận kết quả, escalate nếu chưa đạt | Demo được đúng 1 vòng escalate (chưa đạt → chuyển lên cấp cao hơn) |
| Phân quyền cơ bản | 3 vai trò xem hệ thống khác nhau | Tài khoản demo dựng sẵn cho: sinh viên, cán bộ giảng đường, P.QTTB |

## 4. Phạm vi không triển khai (Out of scope) và cách giả lập

| Hạng mục | Lý do không làm thật | Giải pháp thay thế trong demo |
|---|---|---|
| QR code gắn tại phòng học | Cần triển khai vật lý trong trường, ngoài phạm vi đồ án | Dropdown chọn phòng, coi như đã quét QR |
| Tích hợp thời khóa biểu thật của NEU | Không có quyền truy cập dữ liệu thật của trường | Dữ liệu thời khóa biểu mẫu (seed data), giả định đã tích hợp qua API trong tương lai |
| Phát hiện trùng lặp bằng AI similarity (embedding) | Tốn effort không tương xứng với thời lượng đồ án | So khớp đơn giản theo cặp (vị trí + loại lỗi) bằng truy vấn SQL thông thường |
| Giới hạn số lần escalate, các trường hợp ngoại lệ khác | Không cần thiết để minh họa ý tưởng cốt lõi | Không xử lý, chỉ demo 1 vòng escalate duy nhất |
| Báo cáo thường niên đánh giá vòng đời tài sản | Không thể tích lũy dữ liệu thật qua nhiều năm trong 1 học kỳ | Dựng khung thống kê cơ bản (biểu đồ số ticket theo loại/vị trí) từ dữ liệu seed |
| Bảo mật, xác thực người dùng thật (SSO trường) | Ngoài phạm vi minh họa nghiệp vụ | Đăng nhập demo bằng tài khoản dựng sẵn, không qua hệ thống xác thực thật |

## 5. Dữ liệu demo (seed data)

- 5–10 phòng học mẫu (đủ để minh họa các cấp lỗi khác nhau).
- Một số ticket lịch sử ở nhiều trạng thái: đang xử lý, đã xử lý xong chờ nghiệm thu, đã đóng — để dashboard không trống khi trình bày.
- 1–2 tài khoản demo cho mỗi vai trò: sinh viên, cán bộ giảng đường, P.QTTB.

## 6. Ba màn hình cốt lõi

1. **Form nhập phản ánh (sinh viên)** — nơi thể hiện rõ nhất kết quả AI phân tích ngay trên giao diện.
2. **Dashboard theo dõi ticket (cán bộ/P.QTTB)** — chứng minh cơ chế auto-dispatch hoạt động đúng.
3. **Trang theo dõi tiến độ & nghiệm thu (sinh viên)** — chứng minh vòng đời ticket khép kín, bao gồm cả nhánh escalate.

## 7. Rủi ro khi trình bày và phương án dự phòng

- **Rủi ro:** API gọi AI bị lỗi/rate-limit hoặc mất kết nối mạng khi đang demo trực tiếp trước lớp.
- **Phương án dự phòng:** Chuẩn bị sẵn video quay lại toàn bộ luồng demo thành công, dùng làm phương án thay thế nếu demo trực tiếp gặp sự cố.

## 8. Ghi chú về công cụ hỗ trợ

Nếu nhóm sử dụng công cụ AI (ChatGPT, Claude...) hỗ trợ viết code hoặc tài liệu trong quá trình thực hiện đồ án, cần ghi chú rõ trong báo cáo như một phần của việc quản lý nguồn lực dự án.
