# AWS Lambda Python Migration Agent

An autonomous migration pipeline and GitHub Action designed to upgrade legacy AWS Lambda functions (Python 3.7, 3.8, 3.9) to modern Python runtimes (Python 3.12 / 3.13) on Amazon Linux 2023 (AL2023).

The agent handles deprecated module refactoring, dependency resolution, custom Lambda layer directory realignment, Infrastructure-as-Code (IaC) updates, and automated verification inside official AWS Lambda container images.

---

## Key Features

- **Automated Code Transformation:** Identifies and refactors breaking standard library removals and deprecations (e.g., replacement of removed `distutils`, migration from `datetime.utcnow()` to timezone-aware UTC objects, and PEP 594 removals).
- **Dependency Version Resolution:** Analyzes `requirements.txt` manifests and upgrades pinned packages to modern, secure distributions compatible with Python 3.12+.
- **Custom Lambda Layer Restructuring:** Realigns Python layer directories from legacy runtime paths (e.g., `layers/python/lib/python3.8/`) to the target version (`python3.12/`) so the Lambda runtime can discover installed packages under `/opt`.
- **Infrastructure as Code (IaC) Synchronization:** Updates AWS SAM templates (`template.yaml`), CloudFormation definitions, or Serverless configs to declare the upgraded runtime version.
- **Sandboxed Docker Verification:** Mounts the refactored Lambda code into the official AWS base image (`public.ecr.aws/lambda/python:3.12`) to verify syntax, imports, and mock event execution prior to deployment.
- **CI/CD Integration:** Runs as a GitHub Action triggered via `workflow_dispatch`, automatically opening a detailed Pull Request with verification status and changelogs.

---

## Architecture Flow
Legacy Lambda Function (Python 3.7/3.8/3.9) + SAM Template + Custom Layers
│
▼
[1. IaC & Layer Path Alignment]
(Updates template.yaml & moves layer folders)
│
▼
[2. AI Transformation Engine]
(Refactors code & upgrades requirements.txt)
│
▼
[3. Containerized Verification]
(Executes smoke test in public.ecr.aws/lambda)
│
┌──────────────┴──────────────┐
▼                             ▼
[Passed]                      [Failed]
Opens GitHub Pull Request    Triggers Retry & Self-Healing

---

## Project Structure

```text
lambda-migration-agent/
│
├── .github/
│   └── workflows/
│       └── migration.yml         # GitHub Actions workflow
│
├── mock_repo/                    # Target Lambda package to migrate
│   ├── lambda_function.py        # Lambda handler
│   ├── requirements.txt          # Pinned dependencies
│   ├── template.yaml             # AWS SAM template
│   └── layers/                   # Custom Lambda layer assets
│       └── python/lib/python3.8/
│
├── gemini_engine.py              # LLM migration engine & prompt schemas
├── verifier.py                   # AWS Lambda base container execution tester
├── agent.py                      # Master migration coordinator
└── requirements.txt              # Agent runtime dependencies