---
name: code-change-quality
description: Use when fixing bugs or adding features in an existing codebase with repository-level testing and documentation conventions.
---
# Code Change Quality

1. Leave existing test files unchanged; add or update tests in new files.
2. Add a regression test for each fixed bug, with at least one test per bug.
3. Add type annotations to every parameter and return value of each public function.
4. Record each fix under `## Unreleased` in `CHANGELOG.md` using the repository’s required bullet format.
5. Run the test suite from the project root and verify the new regression tests pass.
