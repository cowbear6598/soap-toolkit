from __future__ import annotations

import argparse
import getpass
import json
import os
from pathlib import Path
import tempfile

from common import SentryError, config_path, validate_base_url, validate_organization


def write_config(path: Path, data: dict[str, str]) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.name == "posix":
        os.chmod(path.parent, 0o700)

    descriptor, temporary_name = tempfile.mkstemp(prefix=".sentry-", dir=path.parent, text=True)
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
    parser = argparse.ArgumentParser(description="Configure read-only Sentry access")
    parser.add_argument("--organization", help="Sentry organization slug")
    parser.add_argument("--base-url", default="https://sentry.io", help="Sentry base URL")
    args = parser.parse_args()

    try:
        token = getpass.getpass("Sentry auth token: ").strip()
        organization = validate_organization(
            args.organization or input("Sentry organization slug: ")
        )
        base_url = validate_base_url(args.base_url)
        if not token:
            raise SentryError("Sentry auth token cannot be empty.")

        path = config_path()
        write_config(
            path,
            {
                "auth_token": token,
                "organization": organization,
                "base_url": base_url,
            },
        )
        print(json.dumps({"configured": True, "config": str(path)}, ensure_ascii=False, indent=2))
    except (SentryError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
