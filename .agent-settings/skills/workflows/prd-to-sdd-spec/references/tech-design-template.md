# Technical Design Document: [Feature/Component Name]

**Spec Reference:** [Link to Confluence Spec Page]
**Author:** [Agent/Author]
**Date:** [Date]
**Status:** Draft | In Review | Approved

---

## 1. Overview

Brief summary of the feature or change, and the problem it solves.

---

## 2. Problem Statement

Describe the current state, the pain point or gap, and why this solution is needed.

---

## 3. Goals & Non-Goals

### Goals
- [ ] Goal 1
- [ ] Goal 2

### Non-Goals
- Out of scope: X
- Future consideration: Y

---

## 4. Architecture Design

High-level architecture diagram or description. Describe how this fits into the existing system.

### System Context
Describe the system boundaries and external actors.

### Component Diagram
(ASCII diagram or description of major components and their relationships)

```
[Component A] ---(request)---> [Component B]
                                     |
                                     v
                              [Component C]
```

---

## 5. Component Design

### [Component 1 Name]
- **Responsibility:** What it does
- **Interface:** How other components interact with it
- **Key decisions:** Any notable design choices

### [Component 2 Name]
- **Responsibility:**
- **Interface:**
- **Key decisions:**

---

## 6. Data Models & Schemas

### [Entity 1]
```
Field        | Type     | Required | Description
-------------|----------|----------|-------------
id           | UUID     | Yes      | Primary key
created_at   | DateTime | Yes      | Creation timestamp
...
```

### Database Changes
- New tables: [list]
- Modified tables: [list]
- Migrations required: Yes / No

---

## 7. API Contracts

### [Endpoint 1: METHOD /path]
**Purpose:** Description

**Request:**
```json
{
  "field": "value"
}
```

**Response (200):**
```json
{
  "result": "value"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource not found

---

## 8. Dependencies & Integrations

| Dependency | Version | Purpose | Notes |
|------------|---------|---------|-------|
| library-x  | ^1.2.0  | ...     | ...   |

### External Services
- [Service Name]: How it's used

---

## 9. Security Considerations

- Authentication/Authorization approach
- Data validation and sanitization
- Sensitive data handling
- Known attack surfaces and mitigations

---

## 10. Performance Considerations

- Expected load / scale
- Caching strategy
- Potential bottlenecks and mitigations
- SLOs/SLAs if applicable

---

## 11. Testing Strategy

### Unit Tests
- Key components to test
- Edge cases to cover

### Integration Tests
- Service interactions to verify

### E2E / Acceptance Tests
- User flows to validate

---

## 12. Implementation Plan

### Phase 1: [Name] (Est. X days)
- [ ] Task 1
- [ ] Task 2

### Phase 2: [Name] (Est. X days)
- [ ] Task 3
- [ ] Task 4

---

## 13. Open Questions & Risks

| ID | Question / Risk | Priority | Owner | Status |
|----|----------------|----------|-------|--------|
| 1  | [Question]     | High     | TBD   | Open   |

---

## 14. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0     | ...  | ...    | Initial draft |
