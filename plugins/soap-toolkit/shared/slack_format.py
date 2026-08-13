import json
import re


ALLOWED_BLOCK_TYPES = {
    "actions",
    "context",
    "divider",
    "header",
    "image",
    "markdown",
    "rich_text",
    "section",
    "video",
}


def load_blocks(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise ValueError(f"blocks_json_not_found: {path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"blocks_json_invalid: line {e.lineno}, column {e.colno}: {e.msg}")

    if isinstance(data, dict) and "blocks" in data:
        data = data["blocks"]
    return data


def strip_code_spans(text):
    return re.sub(r"```.*?```|`[^`]*`", "", text, flags=re.DOTALL)


def validate_mrkdwn_text(text, location, errors, warnings):
    if not isinstance(text, str):
        errors.append(f"{location}: text must be a string")
        return

    if "\r" in text:
        errors.append(f"{location}: use \\n line breaks, not carriage returns")

    visible_text = strip_code_spans(text)
    for marker, name in (("*", "bold"), ("_", "italic"), ("~", "strike")):
        count = len(re.findall(rf"(?<!\\)\{marker}", visible_text))
        if count % 2 == 1:
            errors.append(f"{location}: unbalanced Slack {name} marker '{marker}'")

    if visible_text.count("```") % 2 == 1:
        errors.append(f"{location}: unbalanced code block marker ```")

    if visible_text.count("<") != visible_text.count(">"):
        errors.append(f"{location}: unbalanced angle brackets for Slack links, mentions, or escaped text")

    for match in re.finditer(r"<([^>\n]+)>", visible_text):
        inner = match.group(1)
        if inner.startswith(("http://", "https://", "mailto:")) and " " in inner:
            errors.append(f"{location}: Slack link target contains spaces: <{inner}>")

    if re.search(r"&(?!amp;|lt;|gt;)", visible_text):
        warnings.append(f"{location}: raw '&' should usually be escaped as &amp; in Slack mrkdwn")


def validate_text_object(obj, location, errors, warnings, allowed_types=None, max_len=None):
    allowed = allowed_types or {"mrkdwn", "plain_text"}
    if not isinstance(obj, dict):
        errors.append(f"{location}: text object must be an object")
        return

    text_type = obj.get("type")
    text = obj.get("text")
    if text_type not in allowed:
        errors.append(f"{location}: text.type must be one of {sorted(allowed)}")
    if not isinstance(text, str) or not text:
        errors.append(f"{location}: text.text must be a non-empty string")
        return
    if max_len and len(text) > max_len:
        errors.append(f"{location}: text.text exceeds {max_len} characters")
    if text_type == "mrkdwn":
        validate_mrkdwn_text(text, location, errors, warnings)


def validate_blocks(blocks, errors, warnings):
    if blocks is None:
        return
    if not isinstance(blocks, list):
        errors.append("blocks: must be a JSON array or an object containing a blocks array")
        return
    if len(blocks) > 50:
        errors.append("blocks: Slack messages support at most 50 blocks")

    for index, block in enumerate(blocks):
        location = f"blocks[{index}]"
        if not isinstance(block, dict):
            errors.append(f"{location}: block must be an object")
            continue

        block_type = block.get("type")
        if block_type not in ALLOWED_BLOCK_TYPES:
            errors.append(f"{location}: unsupported or missing block type: {block_type}")
            continue

        if block_type == "divider":
            extra_keys = set(block) - {"type", "block_id"}
            if extra_keys:
                errors.append(f"{location}: divider blocks only support type and block_id, got {sorted(extra_keys)}")
        elif block_type == "section":
            if "text" not in block and "fields" not in block:
                errors.append(f"{location}: section requires text or fields")
            if "text" in block:
                validate_text_object(block["text"], f"{location}.text", errors, warnings, max_len=3000)
            if "fields" in block:
                fields = block["fields"]
                if not isinstance(fields, list) or not fields:
                    errors.append(f"{location}.fields: must be a non-empty array")
                elif len(fields) > 10:
                    errors.append(f"{location}.fields: Slack sections support at most 10 fields")
                else:
                    for field_index, field in enumerate(fields):
                        validate_text_object(field, f"{location}.fields[{field_index}]", errors, warnings, max_len=2000)
        elif block_type == "header":
            validate_text_object(
                block.get("text"),
                f"{location}.text",
                errors,
                warnings,
                allowed_types={"plain_text"},
                max_len=150,
            )
        elif block_type == "context":
            elements = block.get("elements")
            if not isinstance(elements, list) or not elements:
                errors.append(f"{location}.elements: context requires a non-empty elements array")
            elif len(elements) > 10:
                errors.append(f"{location}.elements: Slack context blocks support at most 10 elements")
            else:
                for element_index, element in enumerate(elements):
                    elem_location = f"{location}.elements[{element_index}]"
                    if not isinstance(element, dict):
                        errors.append(f"{elem_location}: element must be an object")
                    elif element.get("type") in {"mrkdwn", "plain_text"}:
                        validate_text_object(element, elem_location, errors, warnings, max_len=3000)
                    elif element.get("type") == "image":
                        if not element.get("image_url") or not element.get("alt_text"):
                            errors.append(f"{elem_location}: image elements require image_url and alt_text")
                    else:
                        errors.append(f"{elem_location}: unsupported context element type: {element.get('type')}")
        elif block_type == "actions":
            elements = block.get("elements")
            if not isinstance(elements, list) or not elements:
                errors.append(f"{location}.elements: actions requires a non-empty elements array")
            elif len(elements) > 25:
                errors.append(f"{location}.elements: Slack actions blocks support at most 25 elements")
        elif block_type == "image":
            if not block.get("image_url") or not block.get("alt_text"):
                errors.append(f"{location}: image blocks require image_url and alt_text")
            if "title" in block:
                validate_text_object(
                    block["title"],
                    f"{location}.title",
                    errors,
                    warnings,
                    allowed_types={"plain_text"},
                    max_len=2000,
                )
        elif block_type == "markdown":
            if not isinstance(block.get("text"), str) or not block.get("text"):
                errors.append(f"{location}: markdown blocks require non-empty text")
            else:
                validate_mrkdwn_text(block["text"], f"{location}.text", errors, warnings)


def validate_slack_format(message=None, blocks=None):
    errors = []
    warnings = []
    if message:
        validate_mrkdwn_text(message, "message", errors, warnings)
    validate_blocks(blocks, errors, warnings)
    return errors, warnings
