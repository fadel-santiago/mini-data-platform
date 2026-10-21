# ORBIT — Documentation, branding and portability audit

Audit date: **21 October 2026**. Scope: documentation changes and static source/configuration review; no container builds, service starts, pipeline runs, dependency installation, media generation or publication.

## Evidence boundaries

- Audited local commit: `e76632b54e5503b4f484366f1ebace142948c258` on `main`.
- GitHub's API resolves the old repository address to **`fadel-santiago/orbit`**; the local `origin` already targets `https://github.com/fadel-santiago/orbit.git`. The rename was not performed by this audit.
- Remote `main` is `575092f5b14dfa885dea6b1916ce36a8802a647c` (`Create LICENSE`). GitHub reports MIT and exposes a `LICENSE` file, which is absent from this local checkout. Do not mistake the local snapshot for the current remote tree.
- [Existing Ubuntu CI run](https://github.com/fadel-santiago/orbit/actions/runs/38993272997): successful, 17 October 2026, commit `575092f`. Read-only status checked; no workflow triggered.
- Previous local verification is recorded in [CHANGELOG.md](../CHANGELOG.md): 4 Python tests, 10 dbt models, 23 dbt tests, 5 business checks, unchanged ingestion replay and retained PostgreSQL data after container recreation. These checks were not repeated here.
- Existing untracked `scripts/video/` content was preserved. No Git fetch/merge, commit, push, remote-setting change or repository rename was performed.

## Platform assessment

| Platform | Confirmed evidence | Still unverified |
|:--|:--|:--|
| macOS | Prior local Docker demonstration and isolated verification; current files use relative bind mounts and named volumes | A new fresh-machine install, minimum resources, all supported macOS versions and CPU variants |
| Linux | The existing GitHub Actions workflow passed on `ubuntu-latest` | Local Docker Engine deployments on other distributions, permissions/SELinux, rootless Docker and ARM64 |
| Windows | PowerShell equivalents in [README.md](../README.md#quick-start) match the Makefile's Docker commands | Actual PowerShell and WSL2 runs, file sharing, mount permissions, filesystem location and path/line-ending edge cases |

The supported execution path is Linux containers, not native Windows containers or a host-Python installation. Docker containers improve environment consistency; they do not establish host portability without execution evidence. No x86-64/ARM64 matrix was run.

## Prioritized findings

### P1 — Resolve before treating publication and setup as complete

1. **Local/remote license mismatch — confirmed, unresolved locally.** The public repository has MIT; the local checkout does not contain its license commit. Reconcile the local branch with remote `main`, preserving the documentation edits and untracked video scripts. No license choice or legal compatibility certification was made. Third-party dependency and asset licensing was not exhaustively assessed.
2. **Volume loss/migration instructions — confirmed; documentation corrected.** `Makefile` implements `clean-data` as `docker compose down -v`: it deletes both `postgres_data` and `dagster_data` for the selected project. The Makefile help text still mentions only PostgreSQL; application/configuration changes are outside this batch. A different directory/project name selects different default named volumes. Retain the previous `COMPOSE_PROJECT_NAME` when moving an existing installation; verify with `docker compose ls` and `docker volume ls` before any reset. Renaming GitHub alone does not rename or migrate volumes.
3. **Undocumented Compose minimum — confirmed; documentation corrected.** The mapping form `env_file: {path, required: false}` requires Compose **2.24.0+**, per [Docker's reference](https://docs.docker.com/reference/compose-file/services/#required). Older Compose releases and legacy `docker-compose` are not validated. Docker Desktop/Engine and Compose must already be installed and running.
4. **Windows setup previously assumed POSIX tools — confirmed documentation gap, runtime portability unverified.** `cp` and the Makefile workflow are not a plain PowerShell setup. The English README now includes direct PowerShell commands and a WSL2 option; neither is claimed as tested.

### P2 — Engineering and reproducibility limits

5. **Build inputs are not fully locked — confirmed.** [requirements.txt](../requirements.txt) pins direct Python packages, but there is no transitive lockfile or hash enforcement. `python:3.12-slim` and `postgres:16-alpine` are mutable tags; `pip install --upgrade pip` and `setuptools>=80` also float. A previously successful build does not prove future byte-for-byte reproducibility. No vulnerability scan or package availability check was run in this batch.
6. **CI coverage is narrower than platform certification — confirmed.** [.github/workflows/ci.yml](../.github/workflows/ci.yml) uses an immutable checkout action SHA, read-only repository permission, ephemeral project names, synthetic example configuration and unconditional resource cleanup. It runs the pipeline and four unit tests on Ubuntu only. It does not explicitly assert zero replay rows, recreate volumes to check persistence, or HTTP-check Streamlit/Dagster. No Windows/macOS/ARM matrix is defined. The four unit tests cover watermark filtering and quality failure handling, not complete source reconciliation.
7. **Local-demo security boundary — confirmed.** Host ports bind to loopback and `.env` is ignored; the tracked example contains public demo credentials. Ingestion, dbt and dashboard share the same database account. Containers have no configured non-root user; Dagster uses its development server. Authentication, least-privilege roles, TLS, backup/restore and security scanning are not established. Loopback binding is not an authentication mechanism. The review checked tracked configuration and ignore rules, not all history or every dependency for secrets/vulnerabilities.
8. **Strict watermarks have reconciliation limits — confirmed by code review.** [ingestion.py](../src/pme_data_stack/ingestion.py) filters `updated_at > watermark`, reads complete CSVs into memory and has no source-deletion reconciliation. Same-timestamp changes or older late-arriving records are skipped. It also writes the maximum timestamp of the current file back to the watermark; an older replacement file can move that watermark backwards. Existing tests do not cover this regression. A follow-up implementation batch should define late-data and monotonic-watermark behavior before broader real-data use.
9. **Data and operational scopes need explicit wording — confirmed; README clarified.** The generator uses a fixed fixture date, but [accounts_receivable.sql](../models/marts/accounts_receivable.sql) uses `current_date`, so invoice ageing changes over time. Local Streamlit region/date filters affect sales; stock and overdue totals remain global. Dagster defines a 06:00 `Europe/Paris` schedule without explicitly setting it to running. A schedule definition does not prove automatic recurring execution.
10. **Installation and bind mounts have limits — confirmed design, host behavior unverified.** Relative `.:/app` mounts avoid hardcoded user paths but require readable/writable shared files. Container-written caches/logs may be root-owned on Linux. Host ports can collide and are configurable; changing a host port must not change the internal PostgreSQL port. `pyproject.toml` advertises Python >=3.11, but the Dockerfile uses 3.12 and `pip install -e .` alone does not declare/install the requirements list. No native-Python support claim is made.

### P3 — International accessibility and branding

11. **French-only supporting material remains — confirmed and inventoried below.** The English README is the main entry point; UI, log text, model descriptions and most guides remain French. Preserve application identifiers while translating prose.
12. **Old-name references remain where deliberate or out of scope.** See the inventory below. Do not rename runtime namespaces merely to match the GitHub slug.

## Branding and reference inventory

Public title: **ORBIT — Data Engineering & Business Intelligence**.

Suggested GitHub description (recommendation only):

> Reproducible data engineering and BI for CRM, ERP and finance exports with Python, PostgreSQL, dbt, Dagster and Streamlit.

Suggested topics: `data-engineering`, `business-intelligence`, `analytics`, `etl`, `data-pipeline`, `data-quality`, `incremental-loading`, `python`, `postgresql`, `sql`, `dbt`, `dagster`, `streamlit`, `docker`, `docker-compose`.

The current GitHub description is already English. Metadata/topics were inspected, not changed.

| Reference | Disposition |
|:--|:--|
| README GitHub/CI links and clone/tree examples | Updated to verified canonical `fadel-santiago/orbit` in both languages |
| Local directory `mini-data-platform` | Not renamed; directory name is independent of branding and can affect Compose project/volume identity |
| Historical `mini-data-platform-verification` in CHANGELOG | Preserved as the actual previously used Compose project name |
| `scripts/video/assemble_live_demo.sh` and `scripts/video/render_orbit_demo.sh` | Existing untracked scripts contain the old GitHub slug; reported, not edited. Do not regenerate media in this batch |
| Compose services, PostgreSQL database/user, `pme_data_stack`, `pme-data-stack` and `pme_daily_pipeline` | Retained runtime identifiers, not obsolete GitHub links; changing them can break profiles, imports, jobs or persisted state |
| Public showcase/video | Existing `fadelsantiago.com/apps/orbit` links retained; the website and previously rendered video were not changed |

## Remaining translation backlog

| Priority | French-only material | Proposed scope |
|:--|:--|:--|
| First | [OPERATIONS.md](../OPERATIONS.md), [SECURITY.md](../SECURITY.md) | English setup/troubleshooting/security guides, retaining optional French versions |
| Next | [ARCHITECTURE.md](../ARCHITECTURE.md), [LEARNING.md](../LEARNING.md) | Architecture rationale, exercises and explanations |
| Next | [PRODUCT.md](../PRODUCT.md), [PORTFOLIO.md](../PORTFOLIO.md) | Requirements, users and technical walkthrough |
| Later | Historical [CHANGELOG.md](../CHANGELOG.md) entries | Preserve dates and evidence; translate without re-certifying results |
| Separate application batch | Streamlit UI, CLI/Makefile help, Dagster logs and model descriptions in `models/marts/schema.yml` | English-facing prose/localization; keep technical IDs and data values stable |

## Lightweight validation and next batch

Only documentation and source/configuration consistency checks are appropriate here. Command inspection is not command execution; past application tests are not new test results. No operating-system certification, current dependency-security clearance or production-readiness claim is made.

Completed checks: local links/anchors, screenshot-file existence and balanced fences passed; `git diff --check` passed; `docker compose --env-file .env.example config --no-env-resolution --quiet` passed with installed Compose 5.3.1 without starting containers or resolving service env files. The public case-study URL returned HTTP 200. GitHub metadata/license/CI status were read only. UI rendering, PowerShell execution, minimum-version execution and native platform installs were not tested.

**Recommended next batch, subject to approval:** reconcile the existing MIT commit with this local branch, translate operations/security guides, then run isolated synthetic smoke tests for Windows/WSL2 and Linux with explicit persistence, service-access and replay assertions. Address the watermark regression in a separately scoped code change with targeted tests. Do not reset existing volumes.
