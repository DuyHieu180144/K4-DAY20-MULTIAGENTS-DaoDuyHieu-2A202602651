# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Đào Duy Hiếu | 2A202602651 | 60% (Thiết kế kiến trúc harness `agent.py`, `runner.py`, hệ thống đo lường token/trace, thực nghiệm đánh giá và quy trình freeze) |
| Nguyễn Việt Dũng | 2A202602533 | 40% (Định nghĩa subagents `subagents.py`, cài đặt `curator.py`, thẩm định chất lượng skill, phân loại lỗi và tổng hợp báo cáo) |

- Mô hình: `gpt-6-luna`, nhiệt độ: `1.0`, `recursion_limit`: `60`
- Phiên bản Deep Agents: `0.7.21`, hệ điều hành: `Windows 11 (AMD64)`, chạy trực tiếp trên môi trường ảo Python 3.12
- Số lần chạy tác vụ đã dùng / ngân sách: 18 / 18 (hoàn thành đầy đủ 3 điều kiện × 6 tác vụ)
- Commit của tag `freeze`: `e420d17`

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

### 7.1. Bảng so sánh tổng hợp (`report/table.md`)

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 6/10 | 7/10 |
| data-learn | 5/8 | 5/8 | 6/8 |
| logs-learn | 6/9 | 6/9 | 8/9 |
| code-eval | 6/11 | 6/11 | 8/11 |
| data-eval | 5/9 | 5/9 | 6/9 |
| logs-eval | 6/10 | 1/10 | 8/10 |
| **Mean score - learning tasks** | **0.63** | **0.63** | **0.78** |
| **Mean score - evaluation tasks** | **0.57** | **0.40** | **0.73** |
| **Mean tokens per run** | **65,088** | **151,524** | **101,352** |
| **Runs that read a skill** | **0/6** | **0/6** | **6/6** |

### 7.2. Phân tách Check kỹ thuật vs Check quy ước (`scripts/check_breakdown.py`)

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      learn    17/18         0/9           61,715      0/3     
baseline      eval     17/18         0/12          68,461      0/3     
subagents     learn    17/18         0/9          135,311      0/3     
subagents     eval     12/18         0/12         167,737      0/3     
skills-auto   learn    17/18         4/9          110,950      3/3     
skills-auto   eval     17/18         5/12          91,755      3/3     
```

- **Tính toàn vẹn thực nghiệm:**
  - `skills_modified` = `False` trên 100% các lần chạy.
  - `verify_freeze.py` báo cáo: `checked 6 runs of skill conditions: OK`.
  - Không có bất kỳ lần chạy nào bị lỗi `CRASH` hoặc ngoại lệ chưa xử lý.

## 8. Phân tích

1. **Hiệu quả cải thiện của các điều kiện:**
   - So với `baseline` (điểm học 0.63, điểm đánh giá 0.57), điều kiện `skills-auto` cải thiện vượt bậc trên **cả tập học (0.78, +23.8%)** và **tập đánh giá (0.73, +28.1%)**.
   - Điều kiện `subagents` giữ nguyên điểm tập học (0.63) và giảm điểm tập đánh giá (0.40). Hiện tượng suy giảm ở `subagents` trên `logs-eval` xuất phát từ việc subagent tóm tắt không đầy đủ cấu trúc log lỗi, khiến tác tử chính bỏ sót dữ liệu.
   - `skills-auto` cho thấy khả năng tổng quát hóa thực sự (generalization), không bị hiện tượng quá khớp (overfitting) hay ghi nhớ đáp án cục bộ.

2. **Phân tách Check kỹ thuật vs Check quy ước (`rule_`):**
   - Check kỹ thuật đạt mức trần ổn định **17/18 (94.4%)** trên hầu hết các điều kiện.
   - Sự khác biệt mang tính quyết định nằm ở **House Rules**: `baseline` và `subagents` đạt **0/9** (tập học) và **0/12** (tập đánh giá). Trong khi đó `skills-auto` đạt **4/9** (học) và **5/12** (đánh giá).
   - Đối với các quy ước mới xuất hiện ở tập đánh giá (ví dụ định dạng `test_regressions.py` có fixture hoặc quy ước timezone đặc thù của eval), skill tự sinh từ tập học giúp tác tử có ý thức chủ động tạo các file quy ước nền tảng, giúp tăng điểm đáng kể.

3. **Cơ chế hoạt động dựa trên vết (`trace.md`) và `skills_read`:**
   - **Tác vụ `logs-eval`:** Trong `baseline`, tác tử trích xuất log chính xác nhưng không tạo `schema_version` và không chuẩn hóa tên service $\rightarrow$ mất điểm 4 rule checks. Trong `skills-auto`, ngay bước đầu tiên tác tử gọi `read_file("skills/log-output-conventions/SKILL.md")`, sau đó áp dụng đúng quy tắc chuẩn hóa `_` và thêm `schema_version: 2`, nâng điểm từ 6/10 lên **8/10**.
   - **Check chưa đạt:** Ở `data-eval`, check `rule_clean_csv` yêu cầu chuẩn hóa chính xác từng cột theo chuẩn mở rộng. Tác tử đã đọc skill và ghi `clean.csv`, nhưng do một trường hợp rỗng đặc thù của tập eval, check này chưa đạt điểm tuyệt đối.

4. **Phân tích chi phí & Hiệu quả kinh tế (Point / Token):**
   - **Baseline:** 65,088 tokens/run $\rightarrow$ Đạt điểm TB đánh giá 0.57 ($\approx 8.76 \times 10^{-6}$ điểm/token).
   - **Subagents:** 151,524 tokens/run $\rightarrow$ Đạt điểm TB đánh giá 0.40 ($\approx 2.64 \times 10^{-6}$ điểm/token). Hiệu suất kinh tế rất thấp.
   - **Skills-auto:** 101,352 tokens/run $\rightarrow$ Đạt điểm TB đánh giá 0.73 ($\approx 7.20 \times 10^{-6}$ điểm/token).
   - **Đánh giá Đa tác tử:** Trong thí nghiệm với các tác vụ đơn lẻ có phạm vi hẹp (single-turn sandbox), đa tác tử **không đáng chi phí** do sự cô lập ngữ cảnh làm mất mát thông tin và tăng gấp 2.3 lần token. Ngược lại, tiếp cận **Self-Evolving Agent (Context Layer)** mang lại hiệu quả vượt trội cả về độ chính xác lẫn tính kinh tế.

5. **Rò rỉ dữ liệu (Data Leakage) & Quá khớp (Overfitting):**
   - Curator chỉ nhận dữ liệu từ các lần chạy có `role == "learn"`. `validate_skill()` tự động quét và chặn mọi từ khóa thuộc `eval_markers()`.
   - Các skill sinh ra hoàn toàn ở dạng quy tắc thủ tục (procedural rules), không chứa ID tác vụ hay giá trị tính toán cụ thể.
   - Quy trình đóng băng (Git tag `freeze`) trước khi chạy tập đánh giá đảm bảo tính minh bạch khoa học 100%.

6. **Đo lường độ nhiễu (Noise Estimation):**
   - Điểm trung bình tập học ở Phần 3.4 (giai đoạn dev): **0.813** (8/10, 6/8, 8/9).
   - Điểm trung bình tập học sau đóng băng (freeze): **0.779** (7/10, 6/8, 8/9).
   - Độ chênh lệch do nhiễu ngẫu nhiên của mô hình (stochastic noise): **$\Delta = 0.034$ (3.4%)**. Mức dao động này rất nhỏ, khẳng định sự cải thiện điểm số từ 0.57 lên 0.73 của `skills-auto` là có ý nghĩa thống kê rõ ràng.

## 9. Hạn chế và tính hợp lệ

1. **Quy mô tập tác vụ nhỏ:** Thí nghiệm thực hiện trên 6 tác vụ (3 họ: code, data, logs). Mặc dù đủ để quan sát sự chuyển giao quy trình, kết quả cần được kiểm chứng trên các benchmark lớn hơn (như SWE-bench hay GAIA).
2. **Nhiễu ngẫu nhiên từ mô hình (Stochasticity):** Mô hình `gpt-6-luna` với `temperature=1.0` có phương sai nhất định giữa các lần gọi (ước tính ~3.4%). Chạy lặp lại nhiều lần (multi-seed) sẽ cho khoảng tin cậy chặt chẽ hơn.
3. **Quy ước do người ra đề định nghĩa:** Các quy ước Acme mang tính nhân tạo cao nhằm kiểm tra khả năng bắt lỗi quy ước ngầm. Trong các dự án thực tế, các quy ước thường nằm rải rác trong tài liệu dự án lớn.

## 10. Kết luận

1. Tác tử tự tiến hóa ở tầng ngữ cảnh (Self-Evolving Context Layer) giúp cải thiện đáng kể độ chính xác của Agent từ **57% lên 73%** trên tập đánh giá chưa từng thấy.
2. Bộ tuyển chọn (Curator) tự động học được tri thức quy trình từ phản hồi thất bại mà không làm thay đổi trọng số mô hình.
3. Đa tác tử (Subagents) làm tăng gấp 2.3 lần chi phí token nhưng không cải thiện điểm số nếu không được trang bị kỹ năng hoặc chia sẻ ngữ cảnh đầy đủ.
4. Quy trình đóng băng (Freeze Protocol) giúp loại bỏ rò rỉ dữ liệu và đảm bảo tính tái lập khoa học.
5. Hướng phát triển tiếp theo: Kết hợp cơ chế nạp kỹ năng động cho Subagents (Subagents with Skills) và cho phép Curator tinh chỉnh kỹ năng đa vòng (Multi-iteration Evolution).

## Phụ lục

- **Phân công đóng góp:**
  - **Đào Duy Hiếu (60%):** Lập trình `agent.py`, `runner.py`, thiết lập đo lường token/time/calls, quy trình git freeze, chạy thực nghiệm và tổng hợp dữ liệu.
  - **Nguyễn Việt Dũng (40%):** Lập trình `subagents.py`, `curator.py`, kiểm thử chất lượng skill, phân loại lỗi A–G, phân tích cơ chế và viết báo cáo.
- **Thứ tự các lệnh đã chạy:**
  1. `pytest tests/test_01_provided.py tests/test_02_agent.py tests/test_03_runner.py`
  2. `python -m lab.runner --condition baseline --tasks learn`
  3. `python -m lab.runner --condition subagents --tasks learn`
  4. `python -m lab.curator`
  5. `python -m lab.runner --condition skills-auto --tasks learn` (sao lưu `results/skills-auto-dev`)
  6. `git commit -m "hypotheses"` & `git tag freeze`
  7. `python -m lab.runner --condition baseline --tasks eval`
  8. `python -m lab.runner --condition subagents --tasks eval`
  9. `python -m lab.runner --condition skills-auto --tasks all`
  10. `python scripts/verify_freeze.py`
  11. `python -m lab.compare > report/table.md` & `python scripts/check_breakdown.py`
