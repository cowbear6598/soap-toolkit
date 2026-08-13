import mimetypes
import os
import subprocess
import sys
import time

from slack_api import fail, slack_api


SLACK_MAX_FILE_BYTES = 1024 * 1024 * 1024


def validate_file_for_upload(file_path):
    if not os.path.exists(file_path):
        fail(f"錯誤：檔案不存在 — {file_path}")
    if not os.path.isfile(file_path):
        fail(f"錯誤：不是一般檔案 — {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size <= 0:
        fail(f"錯誤：檔案是空的 — {file_path}")
    if file_size > SLACK_MAX_FILE_BYTES:
        fail(f"錯誤：檔案超過 Slack 單檔 1GB 限制 — {file_size} bytes")

    return file_size


def upload_file(token, channel_id, file_path, message=None, thread_ts=None, title=None):
    file_size = validate_file_for_upload(file_path)
    file_name = os.path.basename(file_path)
    display_title = title or file_name
    mime_type = mimetypes.guess_type(file_path)[0]

    resp = slack_api(
        token,
        "files.getUploadURLExternal",
        data={"filename": file_name, "length": file_size},
        content_type="form",
    )
    if not resp.get("ok"):
        fail(f"取得上傳 URL 失敗：{resp.get('error', 'unknown')}")

    upload_url = resp["upload_url"]
    file_id = resp["file_id"]

    cmd = ["curl", "-sS", "--fail", "-X", "POST", upload_url, "-F", f"file=@{file_path}"]
    if mime_type:
        cmd[-1] = f"file=@{file_path};type={mime_type}"
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        fail(f"上傳失敗：{result.stderr}")

    complete_data = {
        "files": [{"id": file_id, "title": display_title}],
        "channel_id": channel_id,
    }
    if message:
        complete_data["initial_comment"] = message
    if thread_ts:
        complete_data["thread_ts"] = thread_ts

    resp = slack_api(token, "files.completeUploadExternal", data=complete_data)
    if not resp.get("ok"):
        fail(f"完成上傳失敗：{resp.get('error', 'unknown')}")
    return resp.get("files", [{}])[0] if resp.get("files") else {"id": file_id, "name": file_name}


VIDEO_FILETYPES = {"mp4", "m4v", "mov", "mpeg", "mpg", "avi", "webm", "video"}


def is_video_file(file):
    mimetype = file.get("mimetype") or ""
    filetype = file.get("filetype") or ""
    return mimetype.startswith("video/") or filetype.lower() in VIDEO_FILETYPES


def list_files(token, channel_id=None, types="all", older_than_days=None, limit=100, video_only=True):
    page = 1
    files = []
    ts_to = None
    if older_than_days is not None:
        ts_to = int(time.time() - older_than_days * 86400)

    while True:
        params = {"count": min(limit, 100), "page": page}
        if channel_id:
            params["channel"] = channel_id
        if types:
            params["types"] = types
        if ts_to:
            params["ts_to"] = ts_to

        resp = slack_api(token, "files.list", params=params)
        if not resp.get("ok"):
            fail(f"取得檔案列表失敗：{resp.get('error', 'unknown')}")

        for file in resp.get("files", []):
            if video_only and not is_video_file(file):
                continue
            files.append(file)
        if len(files) >= limit:
            return files[:limit]

        paging = resp.get("paging") or {}
        pages = int(paging.get("pages") or page)
        if page >= pages:
            return files
        page += 1


def delete_file(token, file_id):
    resp = slack_api(token, "files.delete", data={"file": file_id})
    if not resp.get("ok"):
        print(f"刪除失敗 {file_id}: {resp.get('error', 'unknown')}", file=sys.stderr)
        return False
    return True


def summarize_files(files):
    total_size = sum(int(file.get("size") or 0) for file in files)
    return {
        "count": len(files),
        "total_size": total_size,
        "total_size_mb": round(total_size / 1024 / 1024, 2),
    }
