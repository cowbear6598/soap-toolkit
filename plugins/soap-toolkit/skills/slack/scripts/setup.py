from __future__ import annotations

import argparse
import getpass
import json
import os
from pathlib import Path
import sys
import tempfile


PLUGIN_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(PLUGIN_ROOT, "shared"))

from slack_api import SlackConfigError, config_path, load_config, normalize_profile


def write_config(path: Path, data: dict) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.name == "posix":
        os.chmod(path.parent, 0o700)

    descriptor, temporary_name = tempfile.mkstemp(prefix=".slack-", dir=path.parent, text=True)
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
    parser = argparse.ArgumentParser(description="Configure a Slack Bot Token profile")
    parser.add_argument("--profile", help="Profile name, defaults to default")
    args = parser.parse_args()

    try:
        profile_input = args.profile
        if profile_input is None:
            profile_input = input("Slack profile [default]: ").strip() or "default"
        profile = normalize_profile(profile_input)

        token = getpass.getpass("Slack Bot Token (xoxb-...): ").strip()
        if not token.startswith("xoxb-"):
            raise SlackConfigError("Slack Bot Token must start with xoxb-.")

        path = config_path()
        config = load_config(required=False)
        config["profiles"][profile] = {"bot_token": token}
        write_config(path, config)
        print(
            json.dumps(
                {"configured": True, "profile": profile, "config": str(path)},
                ensure_ascii=False,
                indent=2,
            )
        )
    except (SlackConfigError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
