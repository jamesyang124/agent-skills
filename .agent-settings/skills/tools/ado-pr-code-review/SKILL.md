---
name: ado-pr-code-review
description: Perform a security-focused code review on an Azure DevOps PR by URL. Posts inline LOC-level review comments. Checks for PII exposure in public-facing APIs/UI/URLs, missing input validation (XSS/injection), error response structure (must carry 'code' field), and mandatory OWASP/CWE risk coverage (OWASP Top 10, CWE Top 25, OWASP API Top 10, OWASP Mobile Top 10, and OWASP IoT Top 10). Use when asked to review a PR, code review ado PR, security review pull request, or given an Azure DevOps PR URL.
argument-hint: "<azure-devops-pr-url>"
allowed-tools: mcp_azure_devops__repo_get_pull_request_by_id, mcp_azure_devops__repo_get_pull_request_changes, mcp_azure_devops__repo_get_file_content, mcp_azure_devops__repo_create_pull_request_thread, mcp_azure_devops__repo_list_pull_request_threads
---

# Azure DevOps PR Code Review

## ⚙️ Required: install the `diagnose` skill

Install `diagnose` globally for your agent **once**, then it is available in all projects.

### Claude (global)
```bash
mkdir -p ~/.claude/skills/diagnose
curl -fsSL https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/diagnose/SKILL.md \
  -o ~/.claude/skills/diagnose/SKILL.md
# Then add to ~/.claude/CLAUDE.md:
# - **diagnose** (`~/.claude/skills/diagnose/SKILL.md`) — bug diagnosis loop
```

### GitHub Copilot (global)
```bash
mkdir -p ~/.copilot/skills/diagnose
curl -fsSL https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/diagnose/SKILL.md \
  -o ~/.copilot/skills/diagnose/SKILL.md
# Then reference it from your global Copilot instructions file.
```

### Via agent-settings import-skills.sh (project-local)
```bash
# If using this agent-settings repo, import it into a project:
.agent-settings/skills/import-skills.sh claude diagnose     # Claude / Copilot
```

> The diagnose skill must be visible to your agent before proceeding.

---

Security-focused PR review that posts inline LOC-level comments on the diff.

## Arguments

| Token | Meaning |
|---|---|
| an Azure DevOps PR URL | **required** — the PR to review; parsed in Step 1 |

No URL → ask for one before doing anything else.

---

## Step 1 — Parse the PR URL

Extract from the URL:
- `org` — the Azure DevOps organization
- `project` — the team project
- `repo` — the repository name
- `prId` — the pull request ID (integer)

URL patterns:
```
https://dev.azure.com/{org}/{project}/_git/{repo}/pullrequest/{prId}
https://{org}.visualstudio.com/{project}/_git/{repo}/pullrequest/{prId}
```

## Step 2 — Fetch PR metadata and changed files

1. Call `mcp_azure_devops__repo_get_pull_request_by_id` with `{org}`, `{project}`, `{repo}`, `{prId}`
2. Call `mcp_azure_devops__repo_get_pull_request_changes` to get the list of changed files and their diffs
3. For each changed file, call `mcp_azure_devops__repo_get_file_content` to get the full file content at the PR's source branch

## Comment Format

All inline comments must follow this structure, matching the project's existing review style:

```
{severity_emoji} **{Severity} — {Short title}**

{1-3 sentence explanation of the finding and its risk.}

{Optional: code block showing the problematic code snippet for context.}

**Suggestion:** {Concrete fix or alternative approach. Always include either a corrected code block or a specific actionable change — not just "consider fixing this".}

{Action statement: what the author should do or confirm.}
```

> **Rule**: Every comment **must** include a `**Suggestion:**` block with either a corrected code snippet or a specific recommended approach. A finding without a suggestion is incomplete — do not post it.

**Severity levels:**

| Emoji | Level | When to use |
|---|---|---|
| 🔴 | Critical | Security breach, data leak, broken contract, crash path |
| 🟡 | Medium | Logic flaw, misleading behaviour, missing safeguard |
| 🔵 | Minor | Code quality, unnecessary exposure, inconsistency |
| 🔍 | Question | Clarification needed — not necessarily a bug |

**Examples from this project:**

```
🔴 **Critical — PII exposed in public API response**

`accountId` is serialised directly into the response body of a public-facing endpoint.
This field can identify a specific user and must not be exposed without access control.

**Suggestion:** Remove `accountId` from the response DTO, or replace it with an
opaque token/alias that cannot be reverse-mapped to a real account without server-side context.
If the field is required by a specific consumer, move the endpoint behind authentication
and document the access requirement.
```

```
🟡 **Medium — No empty-string guard on `sceneSID`**

If a caller sends `{ "sceneSID": "" }`, this passes the `required` binding check
but will produce an empty FQDN downstream, causing a Route53 error.

**Suggestion:** Add `min=1` to the binding tag to reject empty strings at the handler boundary:
```go
SceneSID string `json:"sceneSID" binding:"required,min=1"`
```
```

```
🔵 **Minor — Raw AWS struct serialised in response**

`"record": r` leaks internal AWS routing fields that callers don't need.

**Suggestion:** Project only the fields consumers actually need:
```go
return gin.H{
    "fqdn":   fqdn,
    "domain": strings.TrimSuffix(fqdn, "."),
    "type":   aws.StringValue(r.Type),
}
```
```

```
🔍 **Question — Is an empty `values` array valid by design?**

The `values` field accepts an empty slice after binding.
Is `{ "values": [] }` a valid caller intent, or should it be rejected early?

**Suggestion:** If empty is invalid, add `min=1` to the binding tag:
```go
Values []string `json:"values" binding:"required,min=1"`
```
If it is valid, add a code comment explaining the design intent so future reviewers understand the choice.
```

---

## Step 3 — Analyze each file

For every changed file apply all required review lenses below (A-H), based on file surface and runtime context. Collect findings as a list of `{filePath, line, severity, title, body}` tuples — **one finding per line**.

Do not post a single overall summary comment. Every finding must be attached to a specific line.

## Baseline Standards (Must Use Latest Version)

Before evaluating findings, use the latest available release of each standard below (do not rely on outdated versions if a newer release exists):

- OWASP Code Review Guide: https://owasp.org/www-project-code-review-guide/assets/OWASP_Code_Review_Guide_v2.pdf
- OWASP Top 10 Web: https://owasp.org/www-project-top-ten/
- CWE Top 25: https://cwe.mitre.org/top25/
- OWASP API Security Top 10: https://owasp.org/API-Security/
- OWASP Mobile Top 10: https://owasp.org/www-project-mobile-top-10/
- OWASP IoT Top 10 / IoT project: https://owasp.org/www-project-internet-of-things/

As of 2026-06 reference points are:

- OWASP Top 10 Web: 2025
- CWE Top 25: 2025 list
- OWASP API Security Top 10: 2023
- OWASP Mobile Top 10: 2024 final release
- OWASP IoT Top 10: latest archived OWASP IoT Top 10 guidance (no newer replacement shown on project page)

If a newer edition is published, use the newer edition immediately.

---

### Lens A — PII Exposure & Regulatory Compliance

**Scope**: Any file that is part of a public-facing API (request/response DTOs, controllers, serializers, GraphQL types, URL route definitions, UI components that render data to end-users).

**Regulatory baseline**: flag any exposure that would violate:
- **GDPR** — personal data of EU residents must not be exposed without lawful basis; data minimisation principle applies
- **CCPA** — personal information of California residents must not be sold or disclosed without disclosure + opt-out mechanism
- **ISO 27001** — access to personal/sensitive information must be controlled, logged, and limited to authorised parties

The table below lists **minimum required fields to check**. It is **not exhaustive** — you must also flag any other field whose name or context suggests it could identify a person or reveal sensitive personal information, even if it is not listed here.

| PII Type | Example field names (non-exhaustive) | Regulation |
|---|---|---|
| Account ID | `accountId`, `account_id`, `htcAccountId`, `htc_account_id` | GDPR, CCPA |
| Email | `email`, `emailAddress`, `email_address` | GDPR, CCPA |
| Phone number | `phone`, `phoneNumber`, `phone_number`, `mobile` | GDPR, CCPA |
| Wallet / crypto address | `walletAddress`, `wallet_address`, `cryptoAddress` | CCPA |
| Date of birth | `dateOfBirth`, `dob`, `date_of_birth`, `birthDate` | GDPR, CCPA |
| Credit card / payment | `cardNumber`, `cvv`, `cvc`, `creditCard`, `pan` | GDPR, CCPA, ISO 27001 |
| Full name (combination risk) | `fullName` combined with other PII fields | GDPR, CCPA |
| National / government ID | `nationalId`, `ssn`, `taxId`, `passportNumber` | GDPR, CCPA |
| Location / biometric data | `ipAddress`, `gpsCoord`, `biometric`, `faceId` | GDPR |
| Device / behavioural identifiers | `deviceId`, `advertisingId`, `userAgent`, `sessionId` | GDPR, CCPA |
| Health / sensitive category data | `healthData`, `diagnosis`, `gender`, `religion`, `ethnicity` | GDPR (special category) |
| Any other identifiable field | `homeAddress`, `mailingAddress`, `employeeId`, etc. | GDPR, CCPA |

**Additionally flag**:
- Bulk export endpoints (no pagination / rate limit) that could enable mass harvesting of personal data — ISO 27001 data leakage risk
- Logs or error responses that include personal data fields — GDPR data minimisation violation
- Unauthenticated endpoints returning any field from the table above — 🔴 Critical under all three regulations
- Missing or insufficient access control on endpoints returning personal data — ISO 27001 A.9 (Access Control)

**Comment template** (use the format defined in "Comment Format" above):
```
🟡 **Medium — PII / Regulatory Risk: `{fieldName}` in public-facing {API / URL / UI}**

`{fieldName}` may expose {pii type}, which is regulated under {GDPR / CCPA / ISO 27001}.
Exposing this without lawful basis, access control, or explicit disclosure may constitute a compliance violation.

**Suggestion:** {Choose one based on context:}
- Remove the field from the response DTO if it is not needed by callers.
- Replace with a masked/truncated value (e.g. last 4 digits, first letter of email domain).
- Move the field to an authenticated-only endpoint and document the lawful basis / access requirement.
- If intentional, add a code comment stating the business reason, lawful basis (GDPR Art. 6), and whether a DPIA is required.
```

Use 🔴 Critical if the field is in an unauthenticated public endpoint. Use 🟡 Medium if behind auth but still potentially over-sharing.

Post the comment on the **line where the field is declared or serialized**.

---

### Lens B — Input Validation & Security

**Scope**: API endpoint handlers, request DTOs, form inputs, URL parameter bindings, query parameters.

Flag when:
- A request body DTO has no validation annotations (e.g. `@NotNull`, `@Size`, `@Pattern`, `Required`, `z.string()`, etc.)
- User-supplied input is passed directly to a database query, HTML renderer, shell command, or template engine without sanitization
- URL or query parameters are reflected back into responses or HTML without encoding
- File upload endpoints lack MIME type / size validation
- String inputs that will be stored and later rendered in UI have no XSS-safe encoding

**Null / empty / undefined guard checks** — flag when any of the following is missing and the absence appears unintentional:
- A string field has no empty-string (`""`) guard — comment if empty string is not a valid design state
- An array/slice/list field has no empty-array (`[]`) guard — comment if an empty collection is not a valid design state
- A value can be `null`, `nil`, `undefined`, or `None` but is used without a nil/null check before access
- A required field has no presence check before it is read or forwarded

For each null/empty finding, **ask the author** whether the empty/nil state is intentional by design. Do not assume it is a bug — treat it as a clarification request.

**Comment template — missing type/length/format validation**:
```
🟡 **Medium — No input validation on `{parameter/field}`**

`{parameter/field}` is user-supplied with no visible type/length/format constraint.
This may allow unexpected values that could lead to XSS or injection.

**Suggestion:** Add validation appropriate to the framework, e.g.:
```{language}
{concrete corrected declaration with validation annotation or binding tag}
```
If validation exists elsewhere in the call chain, add a comment pointing to it.
```

**Comment template — missing null/empty guard**:
```
🔍 **Question — Is {null / empty string / empty array} valid for `{field}`?**

`{field}` can be {nil/null/empty} here with no guard before use.

**Suggestion:** If this state is invalid, add an explicit guard:
```{language}
{concrete nil/empty check with early return or error}
```
If it is intentional by design, add a short comment in the code explaining why
so future reviewers don't flag it again.
```

Post on the **line of the parameter declaration or the first use of the unvalidated / unguarded value**.

---

### Lens C — Error Response `code` Field

**Scope**: Error/exception handlers, error response structs/classes/types, API middleware, HTTP error factories.

Flag when:
- An error response object is defined without a `code` field (at root or nested level)
- An error is returned/thrown where only `message` is set, with no `code`
- A catch block or error handler returns a response body that contains only `message`, `error`, or `description` but no machine-readable `code`
- A caller is reading `.message` from an error response instead of `.code`

**Expected pattern** (any of these is acceptable):
```json
{ "code": "INVALID_INPUT", "message": "..." }
{ "error": { "code": "NOT_FOUND", "message": "..." } }
{ "status": { "code": 4001, "description": "..." } }
```

**Comment template**:
```
🟡 **Medium — Error response missing `code` field**

This error response does not include a `code` field. Callers must be able to identify
error types via a stable `code` (not `message`, which can change with copy/i18n).

**Suggestion:** Add a `code` field at the root or a known nested path:
```{language}
{concrete corrected error response construction with code field added}
```
For example:
```json
{ "code": "INVALID_INPUT", "message": "..." }
{ "error": { "code": "NOT_FOUND", "message": "..." } }
```
```

Use 🔴 Critical if this is a contract-breaking change where a downstream caller currently reads `.code`. Use 🟡 Medium for new endpoints.

Post on the **line where the error response object is constructed or returned**.

---

### Lens D — OWASP Top 10 Web (Latest)

Map changed code to OWASP Top 10 categories and flag applicable issues, with emphasis on:

- Broken access control
- Cryptographic failures
- Injection
- Insecure design
- Security misconfiguration
- Vulnerable/outdated components
- Identification/authentication failures
- Software/data integrity failures
- Security logging/monitoring failures
- SSRF

Rules:

- Use current OWASP Top 10 terminology and IDs from the latest edition.
- If the code introduces one of these risks, post a finding with a concrete exploit path.
- If no category applies for a file, do not force a finding.

Post on the most specific risky line (sink, policy bypass, or insecure config declaration).

---

### Lens E — CWE Top 25 (Latest)

Map findings to CWE IDs from the latest CWE Top 25 list.

Rules:

- Every high-confidence weakness should include at least one CWE mapping (for example `CWE-79`, `CWE-89`, `CWE-22`, `CWE-287`, `CWE-502`).
- Prefer the most specific CWE that matches code behavior.
- If uncertainty is high, use a question-severity comment and ask for clarification before asserting a CWE.

Comment addition requirement:

Add a final line to each applicable comment:
`CWE Mapping: CWE-XXX ({short name})`

---

### Lens F — OWASP API Security Top 10 (Latest)

For API code paths, evaluate against current OWASP API Top 10 categories, including at minimum:

- API1 Broken Object Level Authorization (BOLA)
- API2 Broken Authentication
- API3 Broken Object Property Level Authorization (BOPLA)
- API4 Unrestricted Resource Consumption
- API5 Broken Function Level Authorization
- API6 Unrestricted Access to Sensitive Business Flows
- API7 Server Side Request Forgery
- API8 Security Misconfiguration
- API9 Improper Inventory Management
- API10 Unsafe Consumption of APIs

Flag missing object-level authorization checks, tenant scoping flaws, unconstrained pagination, missing rate limiting, privileged function exposure, and untrusted upstream API handling.

Post on the authorization decision point, route handler, or outbound API consumption line.

---

### Lens G — OWASP Mobile Top 10 (Latest)

When changed code affects mobile apps, SDKs, mobile APIs, or app-backend contracts used by mobile clients, evaluate against the latest OWASP Mobile Top 10.

Check for at least:

- Improper credential usage
- Inadequate supply chain security
- Insecure authentication/authorization
- Insufficient input/output validation
- Insecure communication
- Inadequate privacy controls
- Insufficient binary protections
- Security misconfiguration
- Insecure data storage
- Insufficient cryptography

Flag risky local storage, hardcoded secrets, weak transport/crypto defaults, weak token/session handling, and missing anti-tamper assumptions in client-trusting flows.

Post where the insecure mobile-facing contract, storage usage, credential handling, or crypto/transport config is defined.

---

### Lens H — OWASP IoT Top 10 (Latest Available)

When changed code affects device firmware, embedded services, management planes, device onboarding, OTA update flow, or IoT cloud control APIs, evaluate against OWASP IoT Top 10 guidance (latest available from OWASP IoT project/archive).

Check for at least:

- Weak/guessable/default passwords
- Insecure network services
- Insecure ecosystem interfaces (web/cloud/mobile/API)
- Lack of secure update mechanism
- Use of insecure or outdated components
- Insufficient privacy protection
- Insecure data transfer/storage
- Lack of device management and monitoring
- Insecure default settings
- Lack of physical hardening assumptions where relevant

Flag unauthenticated device actions, unsigned update paths, insecure provisioning, exposed debug/admin interfaces, and missing device identity validation.

Post where trust is established or broken (auth boundary, update verifier, provisioning logic, or control-plane endpoint).

---

## Step 4 — Post inline comments

For each finding:

Call `mcp_azure_devops__repo_create_pull_request_thread` with:
- `pullRequestId`: `{prId}`
- `repositoryId` / `repositoryName`: `{repo}`
- `project`: `{project}`
- Thread status: `active`
- Thread context: `filePath`, `rightFileStartLine` and `rightFileEndLine` set to the finding's line number, `rightFileStartOffset: 1`, `rightFileEndOffset: 1`
- Comment `content`: formatted using the **Comment Format** template above

Post **one thread per finding**. Do not batch multiple findings into one thread.

## Step 5 — Post a summary thread

After all inline comments are posted, create one final thread **without a file/line context** (top-level PR thread) formatted as:

```
## 🔍 Code Review — `{branch-name}`

Automated security-focused review. Findings grouped by severity.

---

### 🔴 Critical ({count})
{list each critical finding: file + short title}

### 🟡 Medium ({count})
{list each medium finding: file + short title}

### 🔵 Minor ({count})
{list each minor finding: file + short title}

### 🔍 Questions ({count})
{list each clarification: file + short title}

---

All findings posted as inline comments. Lenses covered: PII exposure · Input validation · Error code contract · OWASP Top 10 Web · CWE Top 25 · OWASP API Top 10 · OWASP Mobile Top 10 · OWASP IoT Top 10.
```

Omit any severity section that has 0 findings.

## Notes

- Skip binary files, lock files (`*.lock`, `package-lock.json`), and generated files
- If a file has no public-facing surface (e.g. internal utility with no HTTP/UI exposure), skip Lens A for that file but still apply relevant lenses (always B and C; plus D-H where applicable)
- When in doubt about PII risk, **always** leave the comment — it is better to flag and let the author judge than to miss a leak
- Do not flag intentional internal IDs used only in backend-to-backend calls that never reach a client

---

## Using the `diagnose` skill for deep findings

For any finding in Lens B (validation) or Lens C (error contract) where the root cause is **unclear or the fix is non-obvious**, invoke the `diagnose` skill inline before posting the comment:

1. **Phase 1** — build a minimal feedback loop to confirm the vulnerability or broken contract is actually reachable (e.g. craft a curl that triggers the missing validation, or a test that reproduces the missing `code` field)
2. **Phase 3** — generate 2–3 ranked hypotheses for _why_ the issue exists (missing middleware? wrong layer? copy-paste pattern?)
3. Use the confirmed reproduction and ranked hypotheses to make the comment's **Suggestion** block concrete and accurate — not speculative

If you cannot build a feedback loop (e.g. the code path requires a running external service), note this explicitly in the comment:
```
⚠️ Note: Could not build a local repro loop for this finding. The suggestion is based on static analysis only — please verify before applying.
```
