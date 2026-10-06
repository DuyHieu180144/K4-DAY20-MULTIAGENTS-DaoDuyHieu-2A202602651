# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Đào Duy Hiếu | 2A202602651 | 60% (Thiết kế kiến trúc harness `agent.py`, `runner.py`, đo lường token/trace, thực nghiệm đánh giá và quy trình freeze) |
| Nguyễn Việt Dũng | 2A202602533 | 40% (Định nghĩa subagents `subagents.py`, cài đặt `curator.py`, thẩm định skill, phân loại lỗi và tổng hợp báo cáo) |

- Mô hình: `gpt-6-luna`, nhiệt độ: `1.0`, `recursion_limit`: `60`
- Phiên bản Deep Agents: `0.7.21`, hệ điều hành: `Windows 11 (AMD64)`, chạy trực tiếp trên môi trường ảo Python 3.12
- Số lần chạy tác vụ đã dùng / ngân sách: 6 / 18
- Commit của tag `freeze`: (sẽ cập nhật sau khi gắn tag `freeze` ở Phần 4)

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Trên tập tác vụ đánh giá, điều kiện `subagents` sẽ đạt điểm tương đương `baseline` nhưng chi phí token tiêu thụ sẽ cao hơn từ 2 đến 3 lần. Căn cứ: Dữ liệu thực nghiệm tập học cho thấy các subagent bị cô lập ngữ cảnh và không có tri thức về quy ước Acme, do đó chỉ hoàn thành tốt các check kỹ thuật tương tự baseline nhưng tốn thêm nhiều lượt gọi trao đổi.
- H2 (skills-auto so với baseline): Điều kiện `skills-auto` sẽ đạt điểm cao hơn rõ rệt so với `baseline` trên các check quy ước chung (như đơn vị tiền tệ cents, type hints, chuẩn hóa tên service `_`, tạo test hồi quy), tuy nhiên sẽ không tự động giải quyết được các quy ước mới phát sinh riêng của tập đánh giá. Căn cứ từ tài liệu nghiên cứu SkillsBench và SkillEvolBench về việc kỹ năng thủ tục giúp chuẩn hóa quy trình nhưng phụ thuộc vào độ phủ của dữ liệu học.
- H3 (tác vụ học so với tác vụ đánh giá): Điểm số trung bình của điều kiện `skills-auto` trên tác vụ học sẽ cao hơn trên tác vụ đánh giá (xuất hiện khoảng cách tổng quát hóa - generalization gap). Căn cứ: Tác vụ đánh giá thay đổi phân phối dữ liệu và bổ sung quy ước mới mà curator chưa từng quan sát thấy trong phản hồi thất bại của tập học.

## 3. Làm quen Deep Agents (Phần 0.3)

1. **Các công cụ của tác tử mặc định:**
   - Nhóm công cụ tệp (file tools): `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`.
   - Nhóm công cụ thực thi lệnh shell: `execute` (cho phép chạy lệnh shell trong môi trường sandbox cô lập và trả về stdout/stderr/exit code).
   - Nhóm công cụ đa tác tử (subagent): `task` (cho phép khởi tạo và giao nhiệm vụ cho subagent tạm thời).

2. **Mô tả của công cụ `task` về subagent `general-purpose` và ngữ cảnh nhìn thấy:**
   - Về `general-purpose`: Đây là agent đa năng dùng để nghiên cứu các câu hỏi phức tạp, tìm kiếm file/nội dung và thực hiện tác vụ nhiều bước. Agent này có đầy đủ mọi công cụ như agent chính.
   - Về ngữ cảnh nhìn thấy: Mặc định mỗi lần gọi là phi trạng thái (stateless), subagent chỉ nhìn thấy prompt/chỉ dẫn mà agent chính gửi sang và trả về một báo cáo kết quả duy nhất cuối cùng; subagent không tự động nhìn thấy lịch sử hội thoại hay ngữ cảnh trước đó của tác tử chính trừ khi được truyền trực tiếp trong prompt.

3. **System prompt mặc định và trích dẫn hướng dẫn hành vi từ mô tả công cụ:**
   - System prompt mặc định: Rỗng (`''`).
   - Trích câu hướng dẫn từ mô tả của công cụ `task`: *"Put full detail in the prompt and state exactly what it should return"* (hoặc *"The agent's report is not shown to the user; relay a summary yourself"*).
   - Trích câu hướng dẫn từ mô tả của công cụ `execute`: *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."*

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | B (Không kiểm chứng / can thiệp file test gốc) | `the original files in tests/ must not be modified (new test files are allowed)` |
| `code-learn` | `rule_type_hints` | E (Vi phạm quy ước tổ chức) | `RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value.` |
| `code-learn` | `rule_regression_tests` | E (Vi phạm quy ước tổ chức) | `RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass.` |
| `code-learn` | `rule_changelog` | E (Vi phạm quy ước tổ chức) | `RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets).` |
| `data-learn` | `rule_money_in_cents` | E (Vi phạm quy ước tổ chức) | `RULE: money values in answer.json are integer cents (1606.67 USD is written 160667).` |
| `data-learn` | `rule_meta_block` | E (Vi phạm quy ước tổ chức) | `RULE: answer.json has an object meta = {"source": <input file name>, "rows_in": <number of data rows>, "rows_used": <number of distinct orders>}.` |
| `data-learn` | `rule_clean_csv` | E (Vi phạm quy ước tổ chức) | `RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; one row per distinct order with a known amount...` |
| `logs-learn` | `rule_service_names` | E (Vi phạm quy ước tổ chức) | `RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service).` |
| `logs-learn` | `rule_sorted_errors` | E (Vi phạm quy ước tổ chức) | `RULE: errors is sorted by service, then by timestamp_utc, ascending.` |
| `logs-learn` | `rule_schema_header` | E (Vi phạm quy ước tổ chức) | `RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage".` |

**Nhận xét:**
- **Nhóm lỗi chiếm đa số:** Nhóm **E (Vi phạm quy ước tổ chức)** chiếm 90% số lỗi thất bại (9/10 check). Nguyên nhân là các quy ước này (định dạng `meta`, đơn vị tiền tệ cents, quy tắc đặt tên service, schema version, type hints, changelog format) mang tính nội bộ doanh nghiệp của Acme và không được mô tả cụ thể trong đề bài `instruction.md`.
- **Bằng chứng phủ định cho nhóm A–D:** Các check kỹ thuật đạt **17/18 check (94.4%)** (theo `scripts/check_breakdown.py`). Mô hình giải quyết các bài toán logic rất tốt (xử lý múi giờ UTC, chuẩn hóa bảng, parsing log đa dòng, tính toán doanh thu), cho thấy lỗi thất bại không đến từ năng lực hiểu đề hay kỹ thuật cơ bản.
- **Khả năng phòng ngừa của Skill:** Skill hoàn toàn có thể phòng ngừa triệt để nhóm lỗi E bằng cách cung cấp danh sách kiểm tra (checklist) và khuôn mẫu các quy ước tổ chức Acme.

## 5. Điều kiện `subagents` (Phần 2.3)

- **Các subagent đã định nghĩa:**
  - `explorer`: Chuyên đọc tài liệu, kiểm tra cấu trúc dữ liệu và schema mà không chỉnh sửa file.
  - `implementer`: Chuyên thực hiện sửa code, ghi dữ liệu và chạy lệnh test kiểm chứng.
  - `reviewer`: Chuyên độc lập kiểm tra kết quả theo yêu cầu và rà soát các trường hợp biên.
- **`subagent_calls` ở từng tác vụ và nhận xét:**
  - `code-learn`: 2 lần gọi subagent.
  - `data-learn`: 2 lần gọi subagent.
  - `logs-learn`: 1 lần gọi subagent.
  - Tác tử chính đã chủ động phân rã nhiệm vụ và ủy quyền qua công cụ `task` đúng như kỳ vọng của `SUBAGENTS_NOTE`.
- **Thông tin khi giao việc:** Tác tử chính truyền prompt nhiệm vụ tương đối đầy đủ cho subagent (mô tả file cần đọc và yêu cầu cần kiểm tra), tuy nhiên do subagent bị cô lập ngữ cảnh và cũng không biết trước các quy ước Acme nên báo cáo của subagent chỉ tập trung vào khía cạnh kỹ thuật.
- **Ảnh hưởng đến token và thời gian:**
  - Lượng token trung bình tăng từ **61,715 tokens (baseline)** lên **135,311 tokens (subagents)** — tăng khoảng **2.19 lần** (tương ứng +119% chi phí token).
  - Điểm số kỹ thuật giữ nguyên (17/18), điểm quy ước vẫn là 0/9 do subagent không có tri thức bổ sung về quy ước Acme. Do đó đa tác tử thuần túy (chưa có skill) không làm tăng điểm số nhưng làm tăng đáng kể chi phí tính toán.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- **Số lần chạy curator:** 1 lần.
- **Số skill bị xóa:** 0 skill (tất cả 3 skill sinh ra đều đạt chuẩn định dạng, ngắn gọn, súc tích và tuân thủ các ràng buộc bảo mật).

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `code-change-quality` | **Tổng quát:** Quy định quy trình sửa bug, thêm test hồi quy, type hints và cập nhật changelog; không chứa ID hay tên hàm riêng của `code-learn`. | **Đúng:** Khớp chính xác các quy ước Acme (giữ nguyên test gốc, tạo `tests/test_regressions.py`, ghi `CHANGELOG.md` mục Unreleased). | **12 dòng.** `description: Use when fixing bugs or adding features in an existing codebase with repository-level testing and documentation conventions.` $\rightarrow$ `skills_read = 1` ở `code-learn`. |
| `data-output-conventions` | **Tổng quát:** Đưa ra checklist cho xử lý dữ liệu dạng bảng, quy đổi tiền tệ và cấu trúc file xuất ra; không chứa tên cột cụ thể. | **Đúng:** Khớp với quy ước Acme (tiền tệ tính bằng integer cents, tạo `clean.csv`, thêm khối `meta` nguồn và số dòng). | **13 dòng.** `description: Use when cleaning tabular data or producing machine-readable analysis outputs that include money, dates, or metadata.` $\rightarrow$ `skills_read = 1` ở `data-learn`. |
| `log-output-conventions` | **Tổng quát:** Hướng dẫn chuẩn hóa và định dạng log triage thành JSON có cấu trúc; không chứa tên dịch vụ cụ thể. | **Đúng:** Khớp với quy ước Acme (chuẩn hóa service name dấu gạch dưới `_`, sắp xếp theo service và UTC, thêm `schema_version: 2`). | **11 dòng.** `description: Use when parsing logs and producing structured error summaries for downstream consumers.` $\rightarrow$ `skills_read = 1` ở `logs-learn`. |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
