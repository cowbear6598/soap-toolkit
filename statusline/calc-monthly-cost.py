#!/usr/bin/env python3
"""Calculate daily and monthly Claude API cost."""
import json
from pathlib import Path
from datetime import datetime, timezone

claude_dir = Path.home() / ".claude/projects"

now = datetime.now()

# Date ranges
today_start = datetime(now.year, now.month, now.day)
today_end = datetime(now.year, now.month, now.day, 23, 59, 59)
month_start = datetime(now.year, now.month, 1)
if now.month == 12:
    month_end = datetime(now.year + 1, 1, 1)
else:
    month_end = datetime(now.year, now.month + 1, 1)

# Model pricing table ($/1M tokens) - Claude Code always uses latest version
MODEL_PRICING = {
    'opus':   {'input': 5, 'cache_5m': 6.25, 'cache_1h': 10, 'cache_hit': 0.50, 'output': 25},
    'sonnet': {'input': 3, 'cache_5m': 3.75, 'cache_1h': 6,  'cache_hit': 0.30, 'output': 15},
    'haiku':  {'input': 1, 'cache_5m': 1.25, 'cache_1h': 2,  'cache_hit': 0.10, 'output': 5},
}

def get_model_type(model_name):
    """Extract model type from full model name."""
    if not model_name:
        return 'sonnet'

    model_lower = model_name.lower()

    if 'opus' in model_lower:
        return 'opus'
    elif 'haiku' in model_lower:
        return 'haiku'

    return 'sonnet'

# Counters for today and month
today_cost = 0.0
month_cost = 0.0
today_msg_count = 0
month_msg_count = 0

for project_dir in claude_dir.iterdir():
    if not project_dir.is_dir():
        continue

    for jsonl_file in project_dir.glob("*.jsonl"):
        try:
            with open(jsonl_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        timestamp = data.get('timestamp', '')
                        if not timestamp:
                            continue

                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            dt_local = dt.astimezone().replace(tzinfo=None)
                        except:
                            continue

                        if 'message' in data and isinstance(data.get('message'), dict):
                            message = data['message']
                            usage = message.get('usage', {})
                            if not usage:
                                continue

                            # Get model name
                            model_name = message.get('model', '')
                            model_type = get_model_type(model_name)
                            pricing = MODEL_PRICING[model_type]

                            # Parse usage data
                            inp = usage.get('input_tokens', 0)
                            out = usage.get('output_tokens', 0)
                            cache_read = usage.get('cache_read_input_tokens', 0)

                            # Handle cache creation tokens
                            cache_5m = 0
                            cache_1h = 0
                            cache_creation = usage.get('cache_creation', {})

                            if isinstance(cache_creation, dict):
                                # New format with separate 5m and 1h
                                cache_5m = cache_creation.get('ephemeral_5m_input_tokens', 0)
                                cache_1h = cache_creation.get('ephemeral_1h_input_tokens', 0)
                            else:
                                # Old format: treat all cache_creation_input_tokens as 5m
                                cache_5m = usage.get('cache_creation_input_tokens', 0)

                            # Calculate cost for this message
                            msg_cost = (
                                inp * pricing['input'] +
                                out * pricing['output'] +
                                cache_read * pricing['cache_hit'] +
                                cache_5m * pricing['cache_5m'] +
                                cache_1h * pricing['cache_1h']
                            ) / 1_000_000

                            # Check if in this month
                            if month_start <= dt_local < month_end:
                                month_cost += msg_cost
                                month_msg_count += 1

                                # Check if today
                                if today_start <= dt_local <= today_end:
                                    today_cost += msg_cost
                                    today_msg_count += 1

                    except json.JSONDecodeError:
                        pass
        except:
            pass

cache_data = {
    "date": now.strftime("%Y-%m-%d"),
    "month": now.strftime("%Y-%m"),
    "updated": now.isoformat(),
    "today_api_calls": today_msg_count,
    "today_cost": round(today_cost, 2),
    "month_api_calls": month_msg_count,
    "month_cost": round(month_cost, 2)
}

print(json.dumps(cache_data))
