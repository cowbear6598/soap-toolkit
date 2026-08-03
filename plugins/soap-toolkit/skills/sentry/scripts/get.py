from __future__ import annotations

import argparse
from typing import Any
import urllib.parse

from common import SentryError, api_get, load_config, print_json, validate_short_id


SENSITIVE_TAGS = {"email", "ip", "ip_address", "user"}


def tag_map(event: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for tag in event.get("tags") or []:
        if not isinstance(tag, dict):
            continue
        key = str(tag.get("key", ""))
        normalized_key = key.casefold()
        if (
            key
            and normalized_key not in SENSITIVE_TAGS
            and not normalized_key.startswith("user.")
        ):
            result[key] = str(tag.get("value", ""))
    return result


def frame_context(value: Any) -> list[dict[str, Any]]:
    result = []
    if not isinstance(value, list):
        return result
    for item in value:
        if isinstance(item, list) and len(item) == 2:
            result.append({"line": item[0], "code": item[1]})
    return result


def extract_exceptions(event: dict[str, Any]) -> list[dict[str, Any]]:
    exceptions = []
    for entry in event.get("entries") or []:
        if not isinstance(entry, dict) or entry.get("type") != "exception":
            continue
        for exception in (entry.get("data") or {}).get("values") or []:
            if not isinstance(exception, dict):
                continue
            mechanism = exception.get("mechanism") or {}
            frames = []
            for frame in (exception.get("stacktrace") or {}).get("frames") or []:
                if not isinstance(frame, dict):
                    continue
                frames.append(
                    {
                        "module": frame.get("module"),
                        "filename": frame.get("filename"),
                        "function": frame.get("function"),
                        "lineNo": frame.get("lineNo"),
                        "colNo": frame.get("colNo"),
                        "inApp": frame.get("inApp"),
                        "absPath": frame.get("absPath"),
                        "context": frame_context(frame.get("context")),
                    }
                )
            exceptions.append(
                {
                    "type": exception.get("type"),
                    "value": exception.get("value"),
                    "mechanism": {
                        "type": mechanism.get("type"),
                        "handled": mechanism.get("handled"),
                    },
                    "frames": frames,
                }
            )
    return exceptions


def request_summary(event: dict[str, Any]) -> dict[str, Any] | None:
    for entry in event.get("entries") or []:
        if isinstance(entry, dict) and entry.get("type") == "request":
            data = entry.get("data") or {}
            raw_url = data.get("url")
            if isinstance(raw_url, str):
                parsed = urllib.parse.urlsplit(raw_url)
                raw_url = urllib.parse.urlunsplit(
                    (parsed.scheme, parsed.netloc, parsed.path, "", "")
                )
            return {"method": data.get("method"), "url": raw_url}
    return None


def resolve_issue(config: dict[str, str], short_id: str) -> dict[str, Any]:
    organization = urllib.parse.quote(config["organization"], safe="")
    issues = api_get(
        config,
        f"/api/0/organizations/{organization}/issues/",
        {"shortIdLookup": "1", "query": short_id, "limit": "2"},
    )
    if not isinstance(issues, list):
        raise SentryError("Sentry returned an unexpected shortId lookup response.")

    matches = [
        issue
        for issue in issues
        if isinstance(issue, dict)
        and str(issue.get("shortId", "")).casefold() == short_id.casefold()
    ]
    if not matches:
        raise SentryError(f"Sentry issue not found for shortId: {short_id}")
    return matches[0]


def format_issue(issue: dict[str, Any]) -> dict[str, Any]:
    project = issue.get("project") or {}
    return {
        "id": issue.get("id"),
        "shortId": issue.get("shortId"),
        "title": issue.get("title"),
        "culprit": issue.get("culprit"),
        "level": issue.get("level"),
        "status": issue.get("status"),
        "count": issue.get("count"),
        "userCount": issue.get("userCount"),
        "firstSeen": issue.get("firstSeen"),
        "lastSeen": issue.get("lastSeen"),
        "permalink": issue.get("permalink"),
        "project": {
            "slug": project.get("slug"),
            "name": project.get("name"),
            "platform": project.get("platform"),
        },
    }


def format_event(event: dict[str, Any]) -> dict[str, Any]:
    tags = tag_map(event)
    release = event.get("release")
    if isinstance(release, dict):
        release = release.get("version")
    errors = [
        {"type": error.get("type"), "message": error.get("message")}
        for error in event.get("errors") or []
        if isinstance(error, dict)
    ]
    return {
        "eventID": event.get("eventID"),
        "dateCreated": event.get("dateCreated"),
        "title": event.get("title"),
        "message": event.get("message"),
        "environment": tags.get("environment"),
        "release": release or tags.get("release"),
        "transaction": event.get("transaction") or tags.get("transaction"),
        "request": request_summary(event),
        "tags": tags,
        "exceptions": extract_exceptions(event),
        "processingErrors": errors,
    }


def get_issue(short_id: str) -> dict[str, Any]:
    config = load_config()
    lookup = resolve_issue(config, short_id)
    issue_id = str(lookup.get("id", ""))
    if not issue_id.isdigit():
        raise SentryError("Sentry shortId lookup did not return a numeric issue ID.")

    organization = urllib.parse.quote(config["organization"], safe="")
    encoded_id = urllib.parse.quote(issue_id, safe="")
    issue = api_get(
        config,
        f"/api/0/organizations/{organization}/issues/{encoded_id}/",
    )
    event = api_get(
        config,
        f"/api/0/organizations/{organization}/issues/{encoded_id}/events/latest/",
    )
    if not isinstance(issue, dict) or not isinstance(event, dict):
        raise SentryError("Sentry returned an unexpected issue or event response.")
    return {"issue": format_issue(issue), "latestEvent": format_event(event)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Get a Sentry issue and its latest event")
    parser.add_argument("short_id", help="Sentry issue shortId, for example PROJECT-123")
    args = parser.parse_args()

    try:
        print_json(get_issue(validate_short_id(args.short_id)))
    except SentryError as exc:
        print_json({"error": str(exc)})
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
