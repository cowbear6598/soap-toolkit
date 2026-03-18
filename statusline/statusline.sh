#!/bin/bash

# Claude Code Custom Status Line (Simplified)
# Shows: [Model] folder [context bricks] percentage (used/total)

input=$(cat)

# Parse Claude data
model=$(echo "$input" | jq -r '.model.display_name // "Claude"' | sed 's/Claude //')
current_dir=$(echo "$input" | jq -r '.workspace.current_dir // env.PWD')
display_dir=$(basename "$current_dir")

# Get context window data
total_tokens=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')
used_pct_raw=$(echo "$input" | jq -r '.context_window.used_percentage // null')

if [[ "$used_pct_raw" != "null" && -n "$used_pct_raw" ]]; then
    usage_pct=${used_pct_raw%.*}
    used_tokens=$(( (total_tokens * usage_pct) / 100 ))
else
    current_usage=$(echo "$input" | jq -r '.context_window.current_usage // null')
    if [[ "$current_usage" != "null" ]]; then
        input_tokens=$(echo "$current_usage" | jq -r '.input_tokens // 0')
        cache_creation=$(echo "$current_usage" | jq -r '.cache_creation_input_tokens // 0')
        cache_read=$(echo "$current_usage" | jq -r '.cache_read_input_tokens // 0')
        used_tokens=$((input_tokens + cache_creation + cache_read))
    else
        used_tokens=0
    fi
    if [[ $total_tokens -gt 0 ]]; then
        usage_pct=$(( (used_tokens * 100) / total_tokens ))
    else
        usage_pct=0
    fi
fi

used_k=$(( used_tokens / 1000 ))
total_k=$(( total_tokens / 1000 ))

# HSV to RGB 轉換（bash integer 版本）
# H: 0-360, S=100, V=100
# 輸出: "R G B"
hsv_to_rgb() {
    local h=$1
    local r g b
    local hi=$(( h / 60 ))
    local f_num=$(( h % 60 ))
    local q=$(( 255 - (f_num * 255 / 59) ))
    local t=$(( f_num * 255 / 59 ))
    case $hi in
        0) r=255; g=$t;  b=0   ;;
        1) r=$q;  g=255; b=0   ;;
        2) r=0;   g=255; b=$t  ;;
        3) r=0;   g=$q;  b=255 ;;
        4) r=$t;  g=0;   b=255 ;;
        5) r=255; g=0;   b=$q  ;;
        *) r=255; g=0;   b=0   ;;
    esac
    echo "$r $g $b"
}

# Braille dot bit mask（每個 row 的左右 dot）
declare -a ROW_BITS=(0x09 0x12 0x24 0xC0)

# Generate Nyan Cat rainbow wave progress bar (40 cells)
total_bricks=40
if [[ $total_tokens -gt 0 ]]; then
    used_bricks=$(( (used_tokens * total_bricks) / total_tokens ))
else
    used_bricks=0
fi

time_offset=$(date +%s)

brick_line="["

for ((i=0; i<total_bricks; i++)); do
    if (( i < used_bricks - 1 )); then
        # 已使用部分：Braille sine wave + 彩虹顏色

        # 計算 sine wave row（0-3）
        phase_deg=$(( (i * 2 + time_offset) * 45 ))
        phase_mod=$(( phase_deg % 360 ))
        if (( phase_mod < 0 )); then
            phase_mod=$(( phase_mod + 360 ))
        fi

        # sin table (scaled x100): 0,71,100,71,0,-71,-100,-71
        case $(( phase_mod / 45 )) in
            0) sin_val=0   ;;
            1) sin_val=71  ;;
            2) sin_val=100 ;;
            3) sin_val=71  ;;
            4) sin_val=0   ;;
            5) sin_val=-71 ;;
            6) sin_val=-100;;
            7) sin_val=-71 ;;
            *) sin_val=0   ;;
        esac

        # 將 sin_val (-100 ~ 100) 映射到 row (0 ~ 3)
        row=$(( (100 - sin_val) * 3 / 200 ))
        if (( row < 0 )); then row=0; fi
        if (( row > 3 )); then row=3; fi

        # 取得對應 row 的 Braille bit
        bits=${ROW_BITS[$row]}

        # Braille Unicode: U+2800 + bits
        braille_code=$(( 0x2800 + bits ))
        braille_char=$(python3 -c "print(chr($braille_code))")

        # 計算彩虹顏色 H 值
        if (( used_bricks > 1 )); then
            h=$(( i * 360 / (used_bricks - 1) ))
        else
            h=0
        fi
        rgb=$(hsv_to_rgb $h)
        r=$(echo $rgb | cut -d' ' -f1)
        g=$(echo $rgb | cut -d' ' -f2)
        b=$(echo $rgb | cut -d' ' -f3)

        brick_line+="\033[38;2;${r};${g};${b}m${braille_char}\033[0m"

    elif (( i == used_bricks - 1 )); then
        # 已使用部分最後放貓咪 emoji
        brick_line+="🐱"

    else
        # 未使用部分：暗灰色 ·
        brick_line+="\033[38;2;80;80;80m·\033[0m"
    fi
done

brick_line+="]"

# Calculate cost directly (no cache)
today_cost_display=""
monthly_cost_display=""
calc_script="$HOME/.claude/statusline/calc-monthly-cost.py"

# Get cost data from Python script stdout
cost_data=$(python3 "$calc_script" 2>/dev/null)

if [[ -n "$cost_data" ]]; then
    today_cost=$(echo "$cost_data" | jq -r '.today_cost // 0' 2>/dev/null)
    monthly_cost=$(echo "$cost_data" | jq -r '.month_cost // 0' 2>/dev/null)

    if [[ -n "$today_cost" ]]; then
        today_cost_display=" | \033[0;33m\$${today_cost}\033[0m"
    fi
    if [[ -n "$monthly_cost" ]]; then
        monthly_cost_display=" | \033[1;35m\$${monthly_cost}/mo\033[0m"
    fi
fi

# Output single line
echo -e "\033[1;36m[$model]\033[0m \033[1;33m$display_dir\033[0m $brick_line \033[1m${usage_pct}%\033[0m (${used_k}k/${total_k}k)${today_cost_display}${monthly_cost_display}"
