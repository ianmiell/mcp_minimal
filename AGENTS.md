# Repository Guidelines

## Project Structure & Module Organization
- Root contains a single Python entrypoint `mcp.py` implementing a minimal Model Context Protocol (MCP) server that reads JSON-RPC from stdin and writes responses to stdout.
- No external assets or test suite yet; add new modules under a `src/` or `mcp_minimal/` package if the code grows, and place tests in a parallel `tests/` directory.
- Keep protocol-facing logic (request parsing, routing, responses) separated from pure helpers so behavior is easy to test in isolation.

## Build, Test, and Development Commands
- Run the server locally: `python mcp.py` (expects JSON-RPC on stdin; pipe sample requests or use an MCP client).
- Quick syntax check: `python -m py_compile mcp.py`.
- If you introduce a test suite, run `pytest` from the repo root.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation; keep functions small and side-effect aware (pure helpers where possible).
- Use descriptive, snake_case names for functions/variables and UPPER_CASE for constants.
- Prefer explicit imports and type hints for new code paths; keep JSON structures well-shaped and documented near usage.
- Keep stdout-only output contract intact—avoid extraneous prints or logging unless gated behind a debug flag.

## Testing Guidelines
- Add unit tests for new tools and routing branches; place files under `tests/` mirroring module paths (e.g., `tests/test_tools.py`).
- Use `pytest` with Arrange/Act/Assert structure; include table-driven cases for request payload variations (missing ids, unknown methods).
- When adding tools, test both success and fallback responses to maintain protocol stability.

## Commit & Pull Request Guidelines
- Use clear, imperative commit messages (`Add X`, `Fix Y`) and group related changes; keep commits small and reviewable.
- Describe behavior changes in PR descriptions: what changed, why, and how to verify (commands run, sample requests/responses).
- Link issues or tasks when relevant and include before/after notes for protocol responses if they changed.
- Screenshots are not required, but paste sample JSON-RPC inputs/outputs when altering tool behavior.

## MCP Protocol Notes
- Supported methods: `initialize`, `tools/list`, and `tools/call` with the `hello` tool. Preserve response shapes (`jsonrpc`, `id`, `result`) and content arrays.
- Version the server via `serverInfo` in `initialize` responses; bump `version` and document changes in PRs when behavior shifts.
