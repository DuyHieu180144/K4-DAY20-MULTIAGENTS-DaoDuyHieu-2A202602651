"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use when you need to inspect files, examine datasets, read logs or documentation, "
                "or analyze failure symptoms without modifying any files. The explorer returns a factual analysis report."
            ),
            "system_prompt": (
                "You are an exploration and analysis specialist. "
                "Your role is to inspect workspace files, documentation, data schemas, and logs thoroughly. "
                "Provide clear, factual, and concise findings. Do NOT modify any files."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use when you need to write code, modify files, run scripts or tests, and verify technical fixes. "
                "The implementer performs the changes and reports execution results."
            ),
            "system_prompt": (
                "You are an implementation specialist. "
                "Your role is to edit files, write code or data outputs, run validation tests and commands, "
                "and report exactly what was changed and the test results."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use when you need an independent check of the modified files against the task specifications, "
                "edge cases, and house rules before concluding. The reviewer does not modify files."
            ),
            "system_prompt": (
                "You are a quality and compliance reviewer. "
                "Your role is to independently review workspace changes, compare them with task requirements, "
                "check for regression risks, edge cases, and house rules. Do NOT modify any files."
            ),
        },
    ]
