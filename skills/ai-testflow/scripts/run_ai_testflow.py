from __future__ import annotations

import subprocess
from pathlib import Path


def main() -> int:
    repo_root = Path.cwd()
    required = [
        repo_root / "ai-testflow.yml",
        repo_root / "ai_testflow",
        repo_root / "docs" / "prd.md",
        repo_root / "backend" / "tests" / "test_api.py",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        print("AI-TestFlow skill cannot run because required paths are missing:")
        for path in missing:
            print(f"- {path}")
        return 2

    command = ["conda", "run", "-n", "AI-TestFlow", "python", "-m", "ai_testflow", "run"]
    completed = subprocess.run(command, cwd=repo_root, text=True, check=False)
    if completed.returncode != 0:
        print(f"AI-TestFlow CLI failed with exit code {completed.returncode}")
        return completed.returncode

    summary_path = repo_root / "ai-testflow-runs" / "latest" / "inspection-summary.json"
    if not summary_path.exists():
        print(f"AI-TestFlow CLI completed but did not create {summary_path}")
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

