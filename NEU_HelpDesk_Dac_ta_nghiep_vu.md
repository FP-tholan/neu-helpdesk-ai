# Đặc tả nghiệp vụ — Luồng xử lý phản ánh NEU HelpDesk AI

## Sơ đồ tổng quan

```
Sinh viên nhập mô tả
        ↓
AI phân tích & tự điền
        ↓
Có thể tự xử lý? ──Có──→ Gợi ý tự xử lý (Cấp 0) [Kết thúc]
        ↓ Chưa
AI hỏi bổ sung nếu cần
        ↓
Trùng phản ánh khác? ──Có──→ Gộp ticket cũ [Kết thúc]
        ↓ Không
Sinh viên xác nhận gửi
        ↓
Auto-dispatch theo cấp (1 → 2 → 3)
        ↓
Theo dõi xử lý thời gian thực
        ↓
Sinh viên nghiệm thu ──Chưa đạt──→ (quay lại Auto-dispatch, escalate cấp cao hơn)
        ↓ Đạt
Lưu dữ liệu & kết thúc
```

---

## Bước 1 — Sinh viên nhập mô tả

**Actor:** Sinh viên / Giảng viên

**Mô tả:** Người dùng nhập phản ánh bằng ngôn ngữ tự nhiên (text, có thể kèm ảnh). Hệ thống tự động lấy thêm ngữ cảnh sẵn có để giảm số trường phải nhập tay.

**Input:**
- Nội dung mô tả (bắt buộc)
- Ảnh minh họa (tùy chọn)
- Ngữ cảnh tự động: vị trí (quét QR tại phòng hoặc GPS), thời gian, thời khóa biểu hiện tại (nếu sinh viên đăng nhập bằng tài khoản trường)

**Output:** Bản ghi phản ánh thô (raw report) kèm metadata ngữ cảnh.

**Quy tắc nghiệp vụ:**
- Nếu sinh viên quét QR tại phòng, trường "vị trí" được điền sẵn và khóa (không cho sửa) để tránh sai lệch.
- Nếu không có QR, sinh viên chọn vị trí từ danh sách phòng/khu vực có sẵn (tránh nhập tự do gây sai chính tả).

**Trường hợp ngoại lệ:**
- Sinh viên không có ảnh minh họa → vẫn cho phép gửi, nhưng hệ thống có thể hạ độ ưu tiên nếu mô tả quá ngắn (< 10 từ) và yêu cầu bổ sung ở Bước 4.

---

## Bước 2 — AI phân tích & tự điền

**Actor:** Hệ thống AI

**Mô tả:** AI đọc nội dung mô tả và ngữ cảnh, tự động gợi ý phân loại để giảm thao tác nhập liệu.

**Input:** Bản ghi phản ánh thô từ Bước 1.

**Xử lý:**
- Trích xuất: nhóm vấn đề (thiết bị giảng dạy, cơ sở vật chất, vệ sinh...), loại lỗi cụ thể (máy chiếu, điều hòa, bàn ghế...), địa điểm (nếu chưa có từ QR), mức độ ưu tiên sơ bộ.
- Mức độ ưu tiên sơ bộ dựa trên: từ khóa khẩn cấp trong mô tả (VD "đang học", "không mở được cửa") + việc phòng đó có đang trong giờ học theo thời khóa biểu hay không.

**Output:** Bản ghi phản ánh đã gắn nhãn (loại lỗi, vị trí, mức ưu tiên sơ bộ, độ tin cậy của từng nhãn).

**Quy tắc nghiệp vụ:**
- Mỗi nhãn AI gợi ý đi kèm một độ tin cậy (confidence score). Nhãn có độ tin cậy dưới ngưỡng quy định sẽ được đánh dấu "cần xác nhận" ở các bước sau thay vì tự động chốt.

**Trường hợp ngoại lệ:**
- Mô tả bằng tiếng Anh hoặc lẫn ký tự đặc biệt → AI vẫn cố phân tích, nếu độ tin cậy thấp thì chuyển thẳng sang Bước 4 để hỏi rõ thay vì đoán sai.

---

## Bước 3 — Quyết định: Có thể tự xử lý không? (Cấp 0)

**Actor:** Hệ thống AI

**Mô tả:** Trước khi tạo ticket, AI kiểm tra xem vấn đề có nằm trong danh sách lỗi có thể tự khắc phục hay không (VD: wifi chậm, mic hết pin dự phòng đã có sẵn trong phòng, máy tính treo cần khởi động lại).

**Tiêu chí rẽ nhánh:**
- Loại lỗi thuộc "danh mục lỗi tự xử lý" đã được P.QTTB duyệt trước, **và** độ tin cậy phân loại ở Bước 2 đủ cao.
- Nếu cả hai điều kiện đúng → rẽ nhánh **Có** (Bước 3a). Ngược lại → rẽ nhánh **Chưa** (Bước 4).

**Nhánh 3a — Gợi ý tự xử lý (Cấp 0), kết thúc:**
- Hệ thống hiển thị hướng dẫn xử lý nhanh (VD các bước khởi động lại thiết bị).
- Sinh viên có 2 lựa chọn: "Đã xử lý được" (đóng, không tạo ticket) hoặc "Vẫn không được, tạo ticket" (quay lại luồng chính, chuyển sang Bước 4 với thông tin đã có).

**Quy tắc nghiệp vụ:**
- Danh mục lỗi tự xử lý là dữ liệu cấu hình, do P.QTTB quản lý và cập nhật định kỳ — không hard-code trong AI.

---

## Bước 4 — AI hỏi bổ sung nếu cần

**Actor:** Hệ thống AI ↔ Sinh viên

**Mô tả:** Chỉ kích hoạt khi có trường thông tin bắt buộc còn thiếu hoặc độ tin cậy thấp. AI hỏi tối đa 1–2 câu, ưu tiên câu hỏi trắc nghiệm/chọn nhanh thay vì để sinh viên gõ tự do.

**Input:** Danh sách trường còn thiếu / có độ tin cậy thấp từ Bước 2.

**Output:** Mô tả đã được chuẩn hóa, đầy đủ các trường bắt buộc (loại lỗi, vị trí, mức độ ảnh hưởng).

**Quy tắc nghiệp vụ:**
- Giới hạn tối đa 2 lượt hỏi — nếu sau 2 lượt vẫn thiếu, hệ thống tự gán mức ưu tiên mặc định (trung bình) và tiếp tục luồng, không giữ sinh viên lại vô thời hạn.
- Sinh viên luôn có quyền sửa lại mô tả do AI tổng hợp trước khi gửi.

---

## Bước 5 — Kiểm tra phản ánh trùng lặp

**Actor:** Hệ thống AI

**Mô tả:** So khớp phản ánh hiện tại với các ticket đang mở (chưa đóng) theo vị trí + loại lỗi + khoảng thời gian gần đây.

**Tiêu chí trùng lặp (đề xuất, cần P.QTTB duyệt ngưỡng cụ thể):**
- Cùng vị trí (phòng/khu vực), cùng loại lỗi, ticket cũ còn mở trong vòng X giờ gần nhất.
- Độ tương đồng nội dung mô tả vượt ngưỡng similarity quy định.

**Nhánh 5a — Gộp ticket cũ, kết thúc luồng tạo mới:**
- Phản ánh mới được liên kết làm "phản ánh xác nhận thêm" vào ticket cũ, không tạo ticket riêng.
- Số lượng người xác nhận cùng một ticket được dùng làm tín hiệu tăng mức ưu tiên (nhiều người báo cùng lỗi → ưu tiên cao hơn).
- Sinh viên vẫn được theo dõi tiến độ ticket đã gộp như ticket của chính mình.

**Trường hợp ngoại lệ:**
- Nếu hệ thống nhận diện sai (gộp nhầm hai vấn đề khác nhau), sinh viên có nút "Đây là vấn đề khác" để tách ra tạo ticket mới.

---

## Bước 6 — Sinh viên xác nhận gửi

**Actor:** Sinh viên

**Mô tả:** Màn hình xác nhận cuối cùng hiển thị toàn bộ thông tin đã tổng hợp (mô tả, vị trí, loại lỗi, mức ưu tiên, ảnh) để sinh viên rà soát trước khi gửi chính thức.

**Output:** Ticket chính thức được tạo, có mã số theo dõi.

---

## Bước 7 — Auto-dispatch theo cấp (1 → 2 → 3)

**Actor:** Hệ thống

**Mô tả:** Hệ thống tự động định tuyến ticket đến đúng bộ phận xử lý dựa trên mức độ nghiêm trọng và loại lỗi.

**Quy tắc phân cấp:**
| Cấp | Điều kiện | Người nhận |
|---|---|---|
| Cấp 1 | Sự cố tại chỗ, xử lý nhanh trong giờ học (đổi pin mic, cắm lại cáp, mở khóa phòng) | Cán bộ trực giảng đường / lao công tầng |
| Cấp 2 | Hỏng hóc kỹ thuật cần chuyên môn, không xử lý được tại chỗ | Dashboard Phòng Quản trị Thiết bị (P.QTTB) |
| Cấp 3 | Hỏng nặng, cần bảo hành/sửa chữa theo hợp đồng | Đơn vị bảo trì thuê ngoài, qua duyệt 1 nút bấm của P.QTTB |

**Quy tắc nghiệp vụ:**
- Ticket luôn khởi tạo ở cấp thấp nhất phù hợp; chỉ chuyển thẳng lên Cấp 2/3 nếu AI xác định rõ đây là lỗi cần chuyên môn (VD hỏng phần cứng bên trong thiết bị) — tránh dồn hết việc nhỏ lên cấp cao.
- Chuyển từ Cấp 2 lên Cấp 3 bắt buộc phải qua xác nhận thủ công (1 nút duyệt) của P.QTTB, không tự động hoàn toàn — để kiểm soát chi phí hợp đồng bảo trì ngoài.

---

## Bước 8 — Theo dõi xử lý thời gian thực

**Actor:** Sinh viên (xem) / Bộ phận xử lý (cập nhật)

**Mô tả:** Trạng thái ticket được cập nhật theo các mốc: Đã tiếp nhận → Đang xử lý → Đã xử lý xong, chờ nghiệm thu.

**Quy tắc nghiệp vụ:**
- Mỗi mốc chuyển trạng thái có mốc thời gian (timestamp) để phục vụ tính SLA (thời gian xử lý trung bình) trong báo cáo thường niên.
- Nếu ticket ở trạng thái "Đang xử lý" quá lâu so với SLA cấp tương ứng, hệ thống tự động nhắc bộ phận phụ trách (không tự escalate — escalate chỉ xảy ra qua nghiệm thu ở Bước 9).

---

## Bước 9 — Sinh viên nghiệm thu

**Actor:** Sinh viên

**Mô tả:** Sau khi bộ phận xử lý báo "đã xử lý xong", sinh viên xác nhận kết quả có đạt hay không.

**Nhánh 9a — Chưa đạt (feedback loop):**
- Ticket không đóng mà quay lại Bước 7, tự động escalate lên cấp xử lý cao hơn cấp vừa xử lý (Cấp 1 → 2, Cấp 2 → 3).
- Lý do "chưa đạt" do sinh viên nhập được đính kèm vào lịch sử ticket để bộ phận cấp cao hơn có ngữ cảnh, không phải xử lý lại từ đầu.

**Quy tắc nghiệp vụ:**
- Giới hạn tối đa số lần escalate (đề xuất: không escalate vượt quá Cấp 3) — nếu đã ở Cấp 3 mà vẫn chưa đạt, ticket được đánh dấu "cần họp xem xét" thay vì lặp vô hạn.

---

## Bước 10 — Lưu dữ liệu & kết thúc

**Actor:** Hệ thống

**Mô tả:** Ticket đã nghiệm thu đạt được đóng và toàn bộ dữ liệu (thời gian xử lý, số lần escalate, loại lỗi, vị trí, chi phí nếu có) được tích lũy vào kho dữ liệu.

**Output:** Dữ liệu đầu vào cho Báo cáo thường niên đánh giá vòng đời tài sản — phục vụ P.QTTB lập kế hoạch mua sắm, thay thế thiết bị dựa trên tần suất hỏng hóc theo vị trí/loại thiết bị.

---

## Các điểm cần P.QTTB quyết định trước khi triển khai (đưa vào Chặng 2 để thảo luận)

1. Danh mục lỗi thuộc diện "tự xử lý Cấp 0" — ai duyệt, cập nhật theo chu kỳ nào.
2. Ngưỡng độ tin cậy (confidence) tối thiểu để AI tự chốt nhãn phân loại mà không cần hỏi lại.
3. Ngưỡng similarity để coi là phản ánh trùng lặp, và khoảng thời gian "gần đây" tính là bao lâu.
4. SLA thời gian xử lý cho từng cấp (1/2/3) — làm cơ sở để hệ thống tự nhắc khi quá hạn.
5. Số lần escalate tối đa trước khi ticket được đưa ra "họp xem xét" thay vì tiếp tục vòng lặp.
