# ADR: Pydantic Configuration with Environment Variables

## Status
Accepted - Implemented in Phase 2

## Context
Need centralized configuration for HTTP transport with support for environment variables, sensible defaults, and type safety.

## Decision
Use Pydantic BaseModel with Field defaults that read from environment variables:

```python
class ZettelkastenConfig(BaseModel):
    http_host: str = Field(
        default=os.getenv("ZETTELKASTEN_HTTP_HOST", "0.0.0.0")
    )
    http_port: int = Field(
        default=int(os.getenv("ZETTELKASTEN_HTTP_PORT", "8000"))
    )
```

## Rationale
1. **Type Safety**: Pydantic validates types automatically
2. **Environment Variables**: Reads from env with fallback defaults
3. **Single Source of Truth**: All config in one place
4. **Self-Documenting**: Field definitions show defaults and types

## Consequences
### Positive
- Type-safe configuration
- Environment variable support
- Clear defaults
- Validation built-in

### Negative
- Field defaults evaluate at module load time (not instance creation)
- Cannot override env vars in tests after module import
- Must reload module to change env var behavior in tests

## Testing Implications
Pydantic evaluates `Field(default=os.getenv(...))` when the module is first imported. Setting environment variables in tests after import has no effect:

```python
# This pattern FAILS
def test_http_port_from_env(monkeypatch):
    monkeypatch.setenv("ZETTELKASTEN_HTTP_PORT", "9000")
    config = ZettelkastenConfig()  # Already evaluated default at module load
    assert config.http_port == 9000  # FAILS - still 8000
```

Solutions:
1. Use `default_factory=lambda: os.getenv(...)` instead of `default=os.getenv(...)`
2. Reload config module in tests: `importlib.reload(config)`
3. Test environment variable behavior through integration tests

See `http-transport-test-improvements.md` for details.
