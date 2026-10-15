# NEU HelpDesk AI — Contract Audit & Reconciliation

| Thuộc tính | Giá trị                                                                    |
| ---------- | -------------------------------------------------------------------------- |
| **Owner**  | [ALL]                                                                      |
| **Status** | ACTIVE                                                                     |
| **Version**| `v1`                                                                       |
| **Reference** | `02-business-spec.md`, `03-database-design.md`, `05-api-spec.md`        |

***

## 1. Mục đích

Ghi lại các quyết định đối chiếu giữa code hiện tại và contract gốc (`v0`).

Từ đây, ba bên **FE / BE / QA** và tài liệu phải khớp nhau. Mọi thay đổi tiếp theo cần được cập nhật vào file này trước khi triển khai.

***

## 2. Nguyên tắc

1. **Spec là source of truth cho nghiệp vụ**, bao gồm lifecycle, dispatch và phân quyền.
2. **Code convention thắng** ở những phần chỉ mang tính style, ví dụ response envelope, định dạng ID, và kiểu chữ của priority.
3. Không tự ý thay đổi public interface khi chưa cập nhật file này.
4. FE và BE phải sử dụng cùng một version contract.

***

## 3. Ticket Lifecycle — CHỐT

```text
NEW
 │
 │ dispatch
 ▼
ASSIGNED
 │
 │ technician accept
 ▼
IN_PROGRESS
 │
 │ technician resolve
 ▼
WAITING_CONFIRM
 │
 ├── user accept ──▶ CLOSED
 │
 └── user reject
     │
     ▼
 RE_PROCESS
 (priority = HIGH)
 │
 │ technician xử lý lại
 ▼
IN_PROGRESS
```

### Trạng thái ticket

| Status             | Ý nghĩa                                 | Ai set                       |
| ------------------ | --------------------------------------- | ---------------------------- |
| `NEW`              | Vừa tạo, chưa dispatch                  | Backend khi tạo ticket       |
| `ASSIGNED`         | Đã gán team, chờ KTV nhận               | Dispatch engine              |
| `IN_PROGRESS`      | KTV đang xử lý                          | Technician                   |
| `WAITING_CONFIRM`  | KTV báo xong, chờ user nghiệm thu       | Technician                   |
| `CLOSED`           | User chấp nhận kết quả                  | User                         |
| `RE_PROCESS`       | User từ chối, cần xử lý lại             | User, qua hành động reject   |
| `CANCELLED`        | Hủy ticket bởi admin                    | Admin                        |

> `CANCELLED` nằm ngoài phạm vi demo.

### Business rules

- Khi tạo ticket, ghi **2 history**:
  - `None → NEW`: tạo ticket.
  - `NEW → ASSIGNED`: dispatch ticket.
- Khi user reject:
  - Chuyển `WAITING_CONFIRM → RE_PROCESS`.
  - Tăng priority lên `HIGH`.
  - Ghi history kèm lý do reject.
- Khi technician chấp nhận xử lý lại:
  - Chuyển `RE_PROCESS → IN_PROGRESS`.

***

## 4. Category Enum — CHỐT

| Code               | Hiển thị                 | Dispatch mặc định |
| ------------------ | ------------------------ | ----------------- |
| `PROJECTOR`        | Máy chiếu                | Theo building     |
| `COMPUTER`         | Máy tính / Phần mềm      | `T_IT`            |
| `WIFI`             | Mạng / Wifi              | `T_IT`            |
| `MICROPHONE`       | Âm thanh                 | Theo building     |
| `AIR_CONDITIONER`  | Điều hòa / Điện lạnh     | Theo building     |
| `ELECTRICITY`      | Điện / Nước              | Theo building     |
| `FURNITURE`        | Bàn ghế / CSVC           | Theo building     |
| `CLEANING`         | Vệ sinh                  | `T_PSA`           |
| `OTHER`            | Khác                     | `T_ADMIN`         |

***

## 5. Dispatch Rules — CHỐT

Dữ liệu được lưu trong bảng DB `dispatch_rules`.

| Priority | Category             | Building ID             | Team ID    | Ghi chú                 |
| -------- | -------------------- | ----------------------- | ---------- | ----------------------- |
| `10`     | `COMPUTER`, `WIFI`   | `NULL`                  | `T_IT`     | Toàn trường             |
| `10`     | `CLEANING`           | `NULL`                  | `T_PSA`    | Toàn trường             |
| `20`     | `NULL`               | `BLD_A1`, `BLD_A2`      | `T_PSA`    | Áp dụng cho A1 / A2     |
| `20`     | `NULL`               | `BLD_B`                 | `T_QTTB`   | Áp dụng cho building B  |
| `99`     | `NULL`               | `NULL`                  | `T_ADMIN`  | Fallback                |

### Query dispatch

```sql
SELECT team_id
FROM dispatch_rules
WHERE (category IN (:cat, NULL))
  AND (building_id IN (:bld, NULL))
ORDER BY priority ASC
LIMIT 1;
```

***

## 6. Response Envelope — CHỐT

Tất cả endpoint trả về theo envelope thống nhất sau:

### Success

```json
{
  "success": true,
  "data": "<object | array>"
}
```

### Error

```json
{
  "success": false,
  "error": {
    "code": "STRING_CODE",
    "message": "Thông báo lỗi bằng tiếng Việt"
  }
}
```

### Ngoại lệ

Endpoint tạo hoặc cập nhật ticket vẫn bọc kết quả trong `data` để giữ tính đồng nhất.

Không sử dụng key `ticket` như trong spec `v0`.

***

## 7. URL Layout — CHỐT

| Nhóm                       | Prefix             | Role cho phép  |
| -------------------------- | ------------------ | -------------- |
| Auth                       | `/auth/*`          | Public         |
| User dashboard             | `/api/*`           | `USER`         |
| Ticket thao tác của user   | `/tickets/*`       | `USER`         |
| Technician                 | `/technician/*`    | `TECHNICIAN`   |
| Team Lead                  | `/management/*`    | `TEAM_LEAD`    |
| Admin                      | `/admin/*`         | `ADMIN`        |

***

## 8. Priority Enum — CHỐT

Các giá trị priority được chuẩn hóa như sau:

```text
LOW | MEDIUM | HIGH | CRITICAL
```

Quy ước:

- Viết **hoa toàn bộ**.
- FE gửi giá trị uppercase.
- Backend lưu uppercase trong DB.

***

## 9. ID Format — CHỐT

| Entity        | Format                 | Ví dụ                   |
| ------------- | ---------------------- | ----------------------- |
| Building      | `BLD_<CODE>`           | `BLD_A2`                |
| Room          | `ROOM_<BLD>_<NUM>`     | `ROOM_A2_602`           |
| Team          | `T_<CODE>`             | `T_QTTB`                |
| User seed     | `USR_<ROLE>_<NN>`      | `USR_STUDENT_01`        |
| User dynamic  | `USR_TECH_<uuid8>`     | `USR_TECH_A1B2C3D4`     |
| Ticket        | `TCK-YYYYMMDD-NNN`     | `TCK-20261014-001`      |
| History       | `HIS-<uuid4>`          | `HIS-<uuid>`            |

***

## 10. Dev Follow-up

- [ ] RAG-LLM triển khai theo `04-schema-contract.md`.
- [ ] Bổ sung business rules:
  - `BR_AUTO_CLOSE`
  - `BR_ANTI_SPAM`
  - Escalation SLA
- [ ] Bổ sung E2E tests.

***

## 11. Change Log

| Version | Thay đổi                                                              | Ngày          |
| ------- | --------------------------------------------------------------------- | ------------- |
| `v0`    | Contract gốc                                                          | —             |
| `v1`    | Reconcile code ↔ spec, chốt lifecycle mới, category enum, admin URL   | `2026-10-13`  |
