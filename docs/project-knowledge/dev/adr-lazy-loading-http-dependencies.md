# ADR: Lazy Loading HTTP Dependencies

## Status
Accepted - Implemented in Phase 3

## Context
HTTP dependencies (uvicorn, starlette) are only needed when running in HTTP mode, not for default STDIO usage. We want to avoid importing unnecessary modules for STDIO users.

## Decision
Import HTTP dependencies inside the `run()` method only when `transport == "http"`:

```python
if transport == "http":
    import uvicorn  # Lazy import
    if enable_cors:
        from starlette.middleware.cors import CORSMiddleware  # Lazy import
```

## Rationale
1. **Faster Startup**: STDIO mode doesn't import HTTP modules
2. **Smaller Memory Footprint**: No unused modules loaded
3. **Optional Dependencies**: Could make HTTP deps optional in future
4. **Clear Separation**: HTTP code only runs when explicitly requested

## Consequences
### Positive
- STDIO startup remains fast and lightweight
- Clear dependency boundaries
- Easy to make HTTP optional in future

### Negative
- Slightly more complex testing (can't patch at module level)
- Import errors only caught at runtime when HTTP is used

## Testing Implications
Because imports are dynamic, standard mocking patterns fail:
```python
# This FAILS - uvicorn not at module level
@patch('zettelkasten_mcp.server.mcp_server.uvicorn')
def test_http_transport(mock_uvicorn):
    ...
```

Solutions:
1. Patch `sys.modules['uvicorn']` before calling run()
2. Patch `builtins.__import__`
3. Refactor to inject uvicorn dependency

See `http-transport-test-improvements.md` for details.
