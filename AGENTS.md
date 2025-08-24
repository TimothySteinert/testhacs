# agents.md

> **Purpose**: Guide Codex in *maintaining* and *updating* an existing Home Assistant custom integration (HACS-compatible). Focus areas: versioning, file structure hygiene, metadata updates, testing, documentation, and compatibility. UI work is minimal; emphasize backend maintenance best practices.

---

## 1. Agent Role & Goals

Codex should:
- Update version metadata (`manifest.json`, `hacs.json`).
- Ensure only **one** integration exists under `custom_components/DOMAIN/`.
- Follow HACS structure rules and update HACS-specific files as needed.
- Add or refresh documentation (`README.md`).
- Ensure compatibility with recent Home Assistant and HACS changes.
- Improve tests and CI if present or add suggestions inline.

---

## 2. Essential Knowledge & Best Practices

### A. HACS Requirements & Repo Structure
- Integration must reside in `custom_components/INTEGRATION_NAME/`. Only the **first** will be recognized by HACS under that path. :contentReference[oaicite:1]{index=1}  
- `manifest.json` must include the following keys: `domain`, `name`, `version`, `documentation`, `issue_tracker`, `codeowners`. :contentReference[oaicite:2]{index=2}  
- To support UI standards, the integration should be registered under `home-assistant/brands`. :contentReference[oaicite:3]{index=3}

### B. HACS Update Behavior
- HACS displays available updates via UI, similar to core system updates. Maintainers are encouraged to publish GitHub releases or use default branch to surface new versions. :contentReference[oaicite:4]{index=4}  
- Users may manually force re-download of updated integration via HACS UI; a Home Assistant restart may be required. :contentReference[oaicite:5]{index=5}  
- Users sometimes need to clear browser cache for updated integrations to appear in UI. :contentReference[oaicite:6]{index=6}  

### C. Workflow & Development Best Practices
- Scaffold a dev environment with a test HA instance, using symbolic links into `config/custom_components` and running hass locally. :contentReference[oaicite:7]{index=7}  
- Use Cookiecutter or the official integration scaffold to generate structured code, including tests and CI stubs. :contentReference[oaicite:8]{index=8}  
- Always backup before publishing updates—this helps rollback in case of compatibility issues. :contentReference[oaicite:9]{index=9}  

### D. Manual vs HACS Updates
- If integration is in HACS, users receive and install updates via HACS UI. :contentReference[oaicite:10]{index=10}  
- Manual installations require the user to replace files manually and restart HA; updates won’t be managed automatically. :contentReference[oaicite:11]{index=11}  

---

## 3. Agent Instructions for Maintenance Actions

### A. Updating `manifest.json`
```jsonc
{
  "domain": "your_domain",
  "name": "Friendly Integration Name",
  "version": "0.2.0",          # Update to new version
  "documentation": "https://github.com/you/repo",
  "issue_tracker": "https://github.com/you/repo/issues",
  "codeowners": ["@yourhandle"]
}
Inline comments: highlight version bump, ensure other fields are up-to-date and accurate.

B. Updating hacs.json (repo root)
jsonc
Copy
Edit
{
  "name": "Friendly Integration Name",
  "content_in_root": false,
  "render_readme": true,
  "homeassistant": "2025.6.0",  # update to the minimum supported HA version
  "country": ["*"],
  "zip_release": false
}
Inline comments: define each field, update homeassistant as necessary.

C. README Enhancements
Add/update sections:

Changelog / What's New

Compatibility Table (HA versions supported)

Upgrade Instructions (tell users to use HACS UI, clear cache, restart, update via Settings → Updates) 
hacs.xyz
TechBloat
Home Assistant Community
+1

Backup Reminder (before updating) 
Home Assistant

Use bold for UI elements and backticks for code snippets, in alignment with HA docs style.

D. Tests & CI Suggestions
If there is no test suite, suggest adding basic unit tests (e.g., testing async_setup, data coordinator).

Recommend GitHub Actions badge and automation for linting/testing upon pull requests.

E. Development Workflow Notes
Inline guidance: Use symlinks to test changes in local HA instances; run HA in virtualenv or test container. 
Home Assistant Community

Suggest following the scaffold structure for consistency.

4. Inline Commenting Conventions
Python files: # for inline comments; triple-quoted """Docstrings""" at module and function levels.

README.md: HTML comments <!-- Codex: ... --> to instruct generation but not display to end-users.

JSON files: Use // inline comments outside JSON spec in agents.md only, not in actual files.

Example in agents.md:

markdown
Copy
Edit
```jsonc
{
  "version": "0.2.0",  // Codex: bump version for new release
}
yaml
Copy
Edit

---

## 5. Final Codex Prompt Section

> **When performing maintenance**, Codex must:
> - Bump `version` in `manifest.json`.
> - Update `homeassistant` in `hacs.json` if needed.
> - Update README with changelog, update instructions, compatibility info, and backup reminders.
> - Recommend adding or enhance test files and CI config if missing.
> - Ensure repository structure follows only one `custom_components/DOMAIN/`.
> - Use commenting conventions: Python `#`, JSON comments in agents.md only, README HTML comments.
> - Reference online documentation in comments for transparency (e.g., HACS update behavior, structure requirements).

---

## 6. References (embedded in comments)

- HACS requirements & repo structure: :contentReference[oaicite:31]{index=31}  
- HACS update behavior & UI: :contentReference[oaicite:32]{index=32}  
- Dev workflow (symlinks, scaffolds): :contentReference[oaicite:33]{index=33}  
- Manual vs HACS update differences: :contentReference[oaicite:34]{index=34}  
