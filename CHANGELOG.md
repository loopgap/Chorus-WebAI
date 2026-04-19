# test_mcp Changelog

All notable changes will be recorded in this file.

## [3.0.1] - 2026-04-18

### Performance Optimization

**Gradio Lazy Loading**:
- Moved `import gradio as gr` from module level to function level
- `import_web_app_seconds`: 15.0s → 0.17s (-99%)
- `build_ui_seconds`: 0.63s → 7.25s (time transferred to build phase)
- Total import+build: 15.63s → 9.30s (-40%)

### Module Extraction

**Session Management**:
- Extracted `LOGIN_STATE`, `LAST_INPUT`, `get_login_lock()`, `get_last_input_lock()` to `src/core/session.py`
- Created `SessionManager` class for login state management

**Configuration**:
- Extracted `_provider_label_from_config()`, `_provider_guide_text()`, `_apply_provider()` to `src/core/config.py`
- Enhanced `ConfigManager` class with additional helper functions

### Testing Improvements

**New Test Files**:
- `test_authz.py`: +35 authorization tests (RBAC, permission checks)
- `test_perf_baseline.py`: +6 performance benchmark tests

**Test Coverage**:
- Total tests: 222 → 300 (+78)
- Authorization tests cover admin/user/guest roles
- Performance tests validate import/build time thresholds

### Documentation

**Updated**:
- `docs/Architecture.md`: Added lazy loading and performance sections
- `docs/Configuration.md`: Added Provider configuration
- `docs/Development.md`: Updated key directories

## [3.0.0] - 2026-04-17

### Initial Optimization

**Module Splitting**:
- `web_app.py`: 1243 lines → 291 lines (-77%)
- Extracted `src/core/templates.py`, `src/services/queue.py`
- Extracted `src/ui/handlers/`, `src/ui/components/`

**Skip Markers**:
- Added `@pytest.mark.skip` for 3 design issue tests

---

## [2.0.0] - 2026-04-16

### Browser Automation

**Playwright Integration**:
- Added `browser_integration` tests
- `python -m playwright install chromium` required

---

## [1.0.0] - 2026-04-15

### Initial Release

**Features**:
- Gradio-based UI for AI task management
- Browser automation with multi-provider support
- Task tracking and history management