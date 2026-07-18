# Sprint M<major>-<number>: <title>

**Goal:** <Describe the concrete outcome delivered by this Sprint.>

**Architecture:** <State the architecture boundary, unchanged layers, and required dependency direction.>

**Tech Stack:** <List the relevant languages, frameworks, tools, and execution environments.>

## 1. Sprint Objective

This Sprint delivers <concise engineering or research objective>.

Primary outcomes:

- <outcome 1>
- <outcome 2>
- <outcome 3>

## 2. Prerequisites

- <dependent requirement, design, review confirmation, or earlier Sprint>
- <required existing code, schema, configuration, artifact, or runtime capability>
- <environment, index, checkpoint, or policy that must already be resolved>

## 3. Boundaries

Included:

- <included item 1>
- <included item 2>

Excluded:

- <excluded item 1>
- <excluded item 2>

## 4. File and Component Responsibilities

| Path | Action | Responsibility |
|---|---|---|
| `<path>` | Create/Modify | <single authoritative responsibility> |
| `<path>` | Create/Modify | <single authoritative responsibility> |

## 5. Work Packages

### 5.1 <Work Package Name>

Objective:

- <work-package objective>

Implementation checklist:

- [ ] Add or update tests for the required behavior and confirm the expected initial failure when applicable.
- [ ] Implement the smallest contract-compliant change.
- [ ] Preserve the approved package, process, and evidence boundaries.
- [ ] Run targeted verification and then the required reusable checks.
- [ ] Update authoritative documentation and traceability without overstating status.

## 6. Test Design

- Unit tests: <cases>
- Contract tests: <cases>
- Integration tests: <cases and qualified environment>
- Negative paths: <fail-closed cases>
- Regression tests: <protected behavior>

## 7. Verification Commands

```text
<targeted command>
<full reusable test command>
<lint and type-check commands>
<documentation validation command>
```

Record which environment produced each result. Local diagnostics must not be
presented as qualified-host, GPU, experiment-gate, or publication evidence.

## 8. Risks and Controls

| Risk | Control |
|---|---|
| <risk> | <preventive or detective control> |

## 9. Deliverables

- [ ] <code or configuration deliverable>
- [ ] <test deliverable>
- [ ] <documentation or evidence deliverable>

## 10. Completion Record

- Implementation status: <not started/in progress/complete>
- Verification status: <not run/local diagnostic/CI verified/qualified environment verified>
- Deferred external evidence: <none or explicit list>
- Commit or artifact identity: <value or unresolved>
