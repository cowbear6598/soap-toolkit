from __future__ import annotations

import argparse
import getpass
import json
import os
from pathlib import Path
import tempfile

from common import JiraError, config_path, validate_url


def write_config(path: Path, data: dict[str, str]) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.name == "posix":
        os.chmod(path.parent, 0o700)

    descriptor, temporary_name = tempfile.mkstemp(prefix=".jira-", dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.chmod(temporary_name, 0o600)
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Configure read-only Jira Cloud access")
    parser.add_argument("--url", help="Jira Cloud URL, for example https://example.atlassian.net")
    parser.add_argument("--email", help="Jira account email")
    args = parser.parse_args()

    try:
        url = validate_url(args.url or input("Jira URL: "))
        email = (args.email or input("Jira email: ")).strip()
        token = getpass.getpass("Jira API token: ").strip()
        if not email:
            raise JiraError("Jira email cannot be empty.")
        if not token:
            raise JiraError("Jira API token cannot be empty.")

        path = config_path()
        write_config(path, {"url": url, "email": email, "api_token": token})
        print(json.dumps({"configured": True, "config": str(path)}, ensure_ascii=False, indent=2))
    except (JiraError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
