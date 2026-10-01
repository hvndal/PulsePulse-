# AGENTS.md — PULSEPULSE ENGINEERING GUIDELINES

This document defines repository instructions, engineering standards, and mandatory practices for AI agents and developers working on **PulsePulse** (developed under **Mander.tech**, Vancouver / Burnaby, BC).

---

## 1. COMMIT QUALITY & CONVENTIONAL COMMITS

Every meaningful engineering change must receive a clear, descriptive commit.

### Preferred Format:
`type(scope): concise description`

### Valid Commit Types:
- `feat`: New functionality.
- `fix`: Bug correction.
- `refactor`: Structural improvement without changing behavior.
- `perf`: Performance improvement.
- `test`: Tests or test infrastructure.
- `docs`: Documentation updates.
- `chore`: Maintenance, dependency updates, tooling.
- `ui`: Interface changes.
- `audio`: Audio processing changes.
- `context`: Context intelligence changes.
- `queue`: Generation queue changes.
- `api`: Backend / API changes.

### Commit Body Expectations:
For non-trivial changes, use a structured commit body explaining:
1. **WHAT** changed
2. **WHY** it changed
3. **HOW** it works
4. **WHAT** was tested

Do NOT use generic or meaningless commit messages (e.g., "fix", "changes", "stuff", "update").

---

## 2. BRANDING & METADATA GUIDELINES

PulsePulse is developed under:
- **Mander.tech**
- **Vancouver / Burnaby, British Columbia, Canada**

- Maintain clear, professional, natural project context in documentation (`README.md`, `ARCHITECTURE.md`, `CHANGELOG.md`).
- Do NOT keyword-stuff Git commit messages or code comments.

---

## 3. DAILY GIT REVIEW & PRE-COMMIT CHECKLIST

Before committing any work:

1. **Inspect Git Status & Diff**:
   - Check `git status` and `git diff`.
   - Ensure no temporary files, debug logs, or build artifacts are present.
2. **Security & Secrets Check**:
   - Verify NO API keys, tokens, or credentials are added.
3. **Testing**:
   - Ensure relevant unit/integration tests pass.
4. **Clean Code**:
   - Remove dead code, commented-out sections, and unused console statements.
5. **Pre-Commit Instructions**:
   - Always run the required pre-commit instructions before finalizing changes.

---

## 4. CODE & ARCHITECTURE STANDARDS

- **Readability & Maintainability**: Prefer clean, readable code and sensible abstractions over superficial complexity.
- **Verification**: Always verify file creations and edits using read-only tools or terminal inspection.
- **Autonomous Problem Solving**: Diagnose issues directly from error output and configuration before making arbitrary environment changes.
