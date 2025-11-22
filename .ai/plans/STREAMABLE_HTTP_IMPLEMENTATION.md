---
id: 2F7850D8-3E51-456C-AE60-C70BAF323BFB
title: Streamable HTTP Transport Implementation Plan
status: 📝 Draft
date: 2025-11-22
author: aRustyDev
related:
  - FF1F3BCB-1328-41E3-9B7C-60946539384A  # Doc: MCP HTTP Transport Protocols
  - 9282B346-B74A-4522-B79C-690705DC1C92  # ADR: HTTP Transport Architecture
  - 15754957-34F7-418C-8E2A-319175C225C3  # Plan: HTTP Implementation (Legacy)
---

# Streamable HTTP Transport Implementation Plan

**Created:** 2025-11-22
**Status:** 📝 Draft - Awaiting Approval
**Related:** [MCP HTTP Transport Protocols](../../docs/project-knowledge/dev/mcp-http-transport-protocols.md)

---

## Problem Statement

### Current Situation

Our MCP server implements **Legacy HTTP+SSE transport (2024-11-05 spec)** which causes:
- ❌ Zed editor cannot connect (60-second timeout)
- ❌ Modern MCP clients fail with 405 errors
- ⚠️ Deprecated protocol limits future client compatibility

### Root Cause

**Protocol Version Mismatch:**
- Server: Legacy HTTP+SSE with `/sse` (GET) and `/messages/` (POST) endpoints
- Modern Clients (Zed): Expect Streamable HTTP with unified `/mcp` endpoint
- The 405 error on POST `/sse` is **correct** for Legacy mode but incompatible with Modern clients

**Technical Details:** See [mcp-http-transport-protocols.md](../../docs/project-knowledge/dev/mcp-http-transport-protocols.md)

---

## Objectives

### Primary Goal

Implement **Modern Streamable HTTP transport (2025-03-26 spec)** to support all MCP clients.

### Success Criteria

- ✅ Zed connects successfully via HTTP transport (no timeout)
- ✅ Modern clients can use POST /mcp → 202 Accepted flow
- ✅ Backward compatibility with Legacy HTTP+SSE maintained
- ✅ All existing tests pass
- ✅ New transport mode documented and tested
- ✅ Zero breaking changes for STDIO transport

### Non-Goals (Out of Scope)

- ❌ WebSocket transport
- ❌ HTTP/2 or HTTP/3 optimization
- ❌ Deprecating Legacy HTTP+SSE (keep for backward compatibility)
- ❌ Multi-instance coordination or clustering

---

## Technical Approach

### Option 1: Extend FastMCP (Recommended)

**Approach:** Add Streamable HTTP support alongside existing SSE transport.

**Pros:**
- Maintain FastMCP integration
- Minimal code changes
- Easy to upstream contribution

**Cons:**
- May require forking if upstream doesn't accept PR
- Need to understand FastMCP internals

### Option 2: Implement Custom Transport

**Approach:** Create standalone Streamable HTTP transport handler.

**Pros:**
- Full control over implementation
- Can optimize for our use case

**Cons:**
- More code to maintain
- Duplicate session management logic
- Harder to upgrade FastMCP

### Option 3: Switch MCP SDK

**Approach:** Migrate from FastMCP to official MCP Python SDK with Streamable HTTP support.

**Pros:**
- Official support
- Better long-term maintenance

**Cons:**
- Large refactoring required
- Breaking API changes
- Lose FastMCP ergonomics

**Decision:** Start with **Option 1 (Extend FastMCP)** for fastest time-to-value.

---

## Implementation Phases

### Phase 1: Research & Design

**Goal:** Understand requirements and design the implementation.

**Tasks:**
1. Review MCP 2025-03-26 specification in detail
2. Study reference implementations:
   - https://github.com/invariantlabs-ai/mcp-streamable-http
   - https://github.com/ferrants/mcp-streamable-http-python-server
3. Design session management strategy
4. Design endpoint routing architecture
5. Create ADR documenting design decisions

**Deliverables:**
- [ ] ADR: Streamable HTTP Architecture
- [ ] Sequence diagrams for request flows
- [ ] Session management design doc

**Estimated Time:** 4 hours

---

### Phase 2: Add /mcp Endpoint Infrastructure

**Goal:** Create the `/mcp` endpoint structure with routing.

**Tasks:**
1. Create `StreamableHttpTransport` class
2. Add `/mcp` route to Starlette app
3. Implement request method routing (GET, POST, DELETE)
4. Add basic health check for `/mcp` endpoint
5. Add integration tests for endpoint availability

**Files to Create:**
- `src/zettelkasten_mcp/transports/streamable_http.py`
- `tests/test_streamable_http_transport.py`

**Files to Modify:**
- `src/zettelkasten_mcp/server/mcp_server.py` (add transport option)
- `src/zettelkasten_mcp/main.py` (add CLI flag)

**Deliverables:**
- [ ] `/mcp` endpoint responds to GET, POST, DELETE
- [ ] Proper 405 responses for unsupported methods
- [ ] Tests for endpoint routing

**Estimated Time:** 6 hours

---

### Phase 3: Implement Session Management

**Goal:** Handle MCP session lifecycle with header-based session IDs.

**Tasks:**
1. Create `SessionManager` class
2. Implement session creation on first POST
3. Add `Mcp-Session-Id` header parsing
4. Implement session storage (in-memory for MVP)
5. Add session cleanup on DELETE
6. Add session timeout handling

**Files to Create:**
- `src/zettelkasten_mcp/transports/session_manager.py`
- `tests/test_session_manager.py`

**Deliverables:**
- [ ] Sessions created and tracked
- [ ] `Mcp-Session-Id` header validated
- [ ] DELETE terminates sessions
- [ ] Tests for session lifecycle

**Estimated Time:** 8 hours

---

### Phase 4: Implement POST /mcp Handler

**Goal:** Handle client-to-server messages with proper queuing.

**Tasks:**
1. Parse JSON-RPC from POST body
2. Implement message queue per session
3. Return 202 Accepted for queued messages
4. Add content negotiation (Accept header)
5. Support immediate JSON response mode
6. Support SSE initiation from POST

**Files to Modify:**
- `src/zettelkasten_mcp/transports/streamable_http.py`

**Deliverables:**
- [ ] POST /mcp accepts JSON-RPC messages
- [ ] 202 Accepted returned for queued messages
- [ ] Content negotiation works correctly
- [ ] Tests for POST handler

**Estimated Time:** 10 hours

---

### Phase 5: Implement GET /mcp Handler

**Goal:** Establish SSE streams for server-to-client messages.

**Tasks:**
1. Implement SSE stream establishment
2. Integrate with session message queue
3. Send queued messages as SSE events
4. Handle client disconnection gracefully
5. Add connection timeout handling

**Files to Modify:**
- `src/zettelkasten_mcp/transports/streamable_http.py`

**Deliverables:**
- [ ] GET /mcp establishes SSE stream
- [ ] Messages delivered via SSE events
- [ ] Disconnection handled properly
- [ ] Tests for GET handler

**Estimated Time:** 8 hours

---

### Phase 6: Implement DELETE /mcp Handler

**Goal:** Allow explicit session termination.

**Tasks:**
1. Parse `Mcp-Session-Id` header
2. Terminate session and cleanup resources
3. Return 204 No Content on success
4. Return 404 if session not found
5. Close any active SSE streams

**Files to Modify:**
- `src/zettelkasten_mcp/transports/streamable_http.py`

**Deliverables:**
- [ ] DELETE /mcp terminates sessions
- [ ] 204 No Content returned
- [ ] Resources cleaned up
- [ ] Tests for DELETE handler

**Estimated Time:** 4 hours

---

### Phase 7: Backward Compatibility

**Goal:** Ensure Legacy HTTP+SSE still works.

**Tasks:**
1. Keep `/sse` and `/messages/` endpoints active
2. Run full regression test suite
3. Test with mcp-remote using Legacy mode
4. Verify no breaking changes to STDIO transport
5. Update documentation about transport modes

**Files to Test:**
- All existing transport-related tests
- Integration tests with mcp-remote

**Deliverables:**
- [ ] Legacy HTTP+SSE still functional
- [ ] All existing tests pass
- [ ] No regressions in STDIO mode
- [ ] Documentation updated

**Estimated Time:** 4 hours

---

### Phase 8: Configuration & CLI

**Goal:** Make Streamable HTTP configurable.

**Tasks:**
1. Add `--transport streamable-http` CLI flag
2. Add environment variables:
   - `ZETTELKASTEN_MCP_ENDPOINT=/mcp`
   - `ZETTELKASTEN_STREAMABLE_HTTP=true`
3. Update config.py with new settings
4. Add validation for incompatible configs
5. Update documentation

**Files to Modify:**
- `src/zettelkasten_mcp/config.py`
- `src/zettelkasten_mcp/main.py`
- `README.md`

**Deliverables:**
- [ ] CLI flag for Streamable HTTP
- [ ] Environment variable configuration
- [ ] Config validation
- [ ] Documentation updated

**Estimated Time:** 4 hours

---

### Phase 9: Testing with Zed

**Goal:** Verify Zed can connect successfully.

**Tasks:**
1. Start server with Streamable HTTP transport
2. Configure Zed with HTTP transport
3. Test connection establishment
4. Test tool invocation
5. Test resource access
6. Verify no timeouts or errors
7. Document Zed configuration

**Zed Config:**
```json
{
  "context_servers": {
    "zettelkasten": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Deliverables:**
- [ ] Zed connects without timeout
- [ ] All MCP operations work
- [ ] Configuration documented
- [ ] Troubleshooting guide created

**Estimated Time:** 3 hours

---

### Phase 10: Docker & Deployment

**Goal:** Update Docker deployment for Streamable HTTP.

**Tasks:**
1. Update Dockerfile with new environment variables
2. Update docker-compose.yaml
3. Add health check for `/mcp` endpoint
4. Update Traefik routing for `/mcp`
5. Test deployment end-to-end

**Files to Modify:**
- `docker/Dockerfile`
- `docker/docker-compose.yaml`
- `docs/project-knowledge/user/HTTP_USAGE.md`

**Deliverables:**
- [ ] Docker deployment supports Streamable HTTP
- [ ] Health checks working
- [ ] Traefik routing configured
- [ ] Deployment docs updated

**Estimated Time:** 4 hours

---

### Phase 11: Documentation & Examples

**Goal:** Provide comprehensive documentation.

**Tasks:**
1. Update README.md with Streamable HTTP usage
2. Create Streamable HTTP usage guide
3. Add example client code
4. Document migration from Legacy to Modern
5. Update troubleshooting guide
6. Create comparison table of transport modes

**Files to Create:**
- `docs/project-knowledge/user/streamable-http-usage.md`
- `docs/project-knowledge/user/transport-migration-guide.md`

**Files to Update:**
- `README.md`
- `docs/project-knowledge/user/HTTP_USAGE.md`
- `docs/project-knowledge/user/troubleshooting-http-transport.md`

**Deliverables:**
- [ ] Comprehensive usage guide
- [ ] Migration documentation
- [ ] Client examples
- [ ] Troubleshooting updated

**Estimated Time:** 6 hours

---

### Phase 12: Performance & Optimization

**Goal:** Ensure Streamable HTTP is production-ready.

**Tasks:**
1. Add request/response logging
2. Implement rate limiting (optional)
3. Add metrics for session count, message throughput
4. Optimize session cleanup
5. Add connection pooling if needed
6. Load testing with multiple clients

**Deliverables:**
- [ ] Performance metrics available
- [ ] Rate limiting configured
- [ ] Load testing results documented
- [ ] Optimization recommendations

**Estimated Time:** 6 hours

---

### Phase 13: Contribute Upstream (Optional)

**Goal:** Share implementation with FastMCP community.

**Tasks:**
1. Clean up code for upstream standards
2. Add comprehensive docstrings
3. Create PR for FastMCP repository
4. Respond to code review feedback
5. Update our fork/dependency based on upstream decision

**Deliverables:**
- [ ] PR submitted to FastMCP
- [ ] Code review addressed
- [ ] Dependency strategy decided

**Estimated Time:** 8 hours (if upstream accepted)

---

## Risk Assessment

### High Risk

**Risk:** Session management bugs causing memory leaks
- **Mitigation:** Implement session timeout and cleanup
- **Testing:** Load test with session churn

**Risk:** Breaking backward compatibility
- **Mitigation:** Comprehensive regression testing
- **Testing:** Test matrix for all transport modes

### Medium Risk

**Risk:** Performance degradation with many concurrent sessions
- **Mitigation:** Session pooling and cleanup
- **Testing:** Load testing with 100+ concurrent sessions

**Risk:** Zed client has additional undocumented requirements
- **Mitigation:** Test early and iterate
- **Testing:** Real-world testing with Zed

### Low Risk

**Risk:** FastMCP upstream rejects PR
- **Mitigation:** Maintain fork if needed
- **Impact:** More maintenance burden but functional

---

## Testing Strategy

### Unit Tests

- [ ] Session manager CRUD operations
- [ ] POST /mcp request parsing
- [ ] GET /mcp SSE stream
- [ ] DELETE /mcp session termination
- [ ] Header validation and parsing

### Integration Tests

- [ ] Full MCP initialize-request-response flow
- [ ] Session lifecycle end-to-end
- [ ] Multiple concurrent sessions
- [ ] Legacy HTTP+SSE regression tests

### Manual Tests

- [ ] Zed connection and tool usage
- [ ] mcp-remote with Streamable HTTP
- [ ] Claude Desktop (if supports Streamable HTTP)
- [ ] Direct curl/httpie testing

### Performance Tests

- [ ] 10 concurrent sessions
- [ ] 100 concurrent sessions
- [ ] Session creation/deletion throughput
- [ ] Message latency under load

---

## Timeline Estimate

| Phase | Estimated Time | Cumulative |
|-------|---------------|-----------|
| 1. Research & Design | 4 hours | 4 hours |
| 2. /mcp Endpoint | 6 hours | 10 hours |
| 3. Session Management | 8 hours | 18 hours |
| 4. POST Handler | 10 hours | 28 hours |
| 5. GET Handler | 8 hours | 36 hours |
| 6. Backward Compat | 4 hours | 40 hours |
| 7. Config & CLI | 4 hours | 44 hours |
| 8. Zed Testing | 3 hours | 47 hours |
| 9. Docker Deploy | 4 hours | 51 hours |
| 10. Documentation | 6 hours | 57 hours |
| 11. Performance | 6 hours | 63 hours |
| 12. Upstream (opt) | 8 hours | 71 hours |

**Total Estimated Time:** 63-71 hours (8-9 days of focused work)

**Recommended Schedule:**
- Week 1: Phases 1-5 (Core implementation)
- Week 2: Phases 6-9 (Integration & testing)
- Week 3: Phases 10-12 (Polish & optimization)

---

## Dependencies

### External Libraries

Current:
- `mcp[cli]>=1.2.0` (has FastMCP)
- `starlette>=0.27.0`
- `uvicorn>=0.23.0`

Potentially Needed:
- None (all required libraries already installed)

### Knowledge Requirements

- MCP 2025-03-26 specification understanding
- SSE protocol and async Python
- Starlette routing and middleware
- Session management patterns

---

## Acceptance Criteria

### Must Have (MVP)

- [x] Research complete and design documented
- [ ] `/mcp` endpoint handles POST, GET, DELETE
- [ ] Session management working correctly
- [ ] Zed connects successfully without timeout
- [ ] Legacy HTTP+SSE still functional
- [ ] All tests passing
- [ ] Documentation updated

### Should Have

- [ ] Performance optimizations applied
- [ ] Rate limiting implemented
- [ ] Comprehensive error handling
- [ ] Production deployment tested

### Nice to Have

- [ ] FastMCP upstream PR accepted
- [ ] Multi-instance session sharing
- [ ] WebSocket transport exploration

---

## Success Metrics

**Primary:**
- ✅ Zed connection time < 5 seconds
- ✅ Zero timeouts in Zed
- ✅ 100% backward compatibility
- ✅ All existing tests pass

**Secondary:**
- ⭐ Session overhead < 1MB per session
- ⭐ Message latency < 100ms p99
- ⭐ Support 50+ concurrent sessions

---

## Related Documentation

- [MCP HTTP Transport Protocols](../../docs/project-knowledge/dev/mcp-http-transport-protocols.md)
- [ADR: HTTP Transport Architecture](../../docs/project-knowledge/dev/adr-http-transport-architecture.md)
- [HTTP Implementation Plan (Legacy)](./HTTP_IMPLEMENTATION.md)

---

## Next Actions

1. **Review & Approve Plan** - Stakeholder sign-off
2. **Prioritize in Backlog** - Determine sprint assignment
3. **Begin Phase 1** - Research & design when approved

---

**Last Updated:** 2025-11-22
**Status:** 📝 Awaiting approval to begin implementation
**Estimated Completion:** 8-9 days after start
