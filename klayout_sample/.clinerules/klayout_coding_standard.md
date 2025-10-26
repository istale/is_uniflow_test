# 🧩 KLayout Coding Standard & JSON I/O Template

> 本檔案放置於 `.clinerules/` 目錄下，作為 Cline 在生成與修改 KLayout 腳本時的行為依據。  
> 適用於所有 `klayout -b -r ... -rd input_parameter=...` 形式的腳本。

---

## 🎯 目的
統一 KLayout 相關程式碼（shell wrapper + Python 腳本）的設計規範，  
確保在多引擎環境下，Cline 生成的程式能保持相同的結構、輸入輸出協定與錯誤回報格式。

---

## 📂 適用範圍
- 所有以 `klayout -b -r` 方式執行的 Python 腳本  
- 相關 shell wrapper（通常位於 `adapters/klayout_py/` 或 `scripts/`）  
- 任意由 Cline 產生或修改、需與 KLayout 溝通的腳本模組

---

## 🧩 一、Shell Wrapper 標準範本
```bash
#!/usr/bin/env bash
# run_klayout_task.sh
# 用途：將參數字串（JSON 或逗號分隔）傳給 KLayout Python 腳本。
# 當User的

if [ $# -lt 1 ]; then
  echo "Usage: $0 '<json_or_csv_string>'"
  exit 1
fi
# Use specific KLayout path
KLAYOUT_PATH="/Applications/KLayout.app/Contents/MacOS/klayout"

INPUT_PARAMETER="$1"

# 假設腳本為 klayout_task.py
$KLAYOUT_PATH -b -r path/to/klayout_task.py -rd input_parameter="${INPUT_PARAMETER}"
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo "{"ok":false,"error":"KLayout exited with code ${EXIT_CODE}"}"
  exit $EXIT_CODE
fi
```

> **無外部參數需求時怎麼辦？**  
> 若任務不需要使用者輸入，可在 wrapper 內預設一份 JSON 字串（例如 `'{"task_id":"static"}'` 或 `'{}'`），並允許覆寫：
> ```bash
> PAYLOAD="${1:-'{}'}"
> klayout -b -r path/to/script.py -rd input_parameter="${PAYLOAD}"
> ```

### 🔄 Shell Wrapper JSON I/O 擴充範本
> 適用於採用 JSON I/O 模式的 Python 腳本；支援讀檔、輸出捕捉與統一錯誤格式。

```bash
#!/usr/bin/env bash
# run_klayout_task_json.sh
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 '<json_string_or_path>' [capture.json]" >&2
  exit 1
fi

RAW_ARG="$1"
if [ -f "$RAW_ARG" ]; then
  INPUT_PARAMETER="$(cat "$RAW_ARG")"
else
  INPUT_PARAMETER="$RAW_ARG"
fi

KLAYOUT_SCRIPT="path/to/klayout_json_io_template.py"
CAPTURE_FILE="${2:-}"

set +e
KLAYOUT_STDOUT="$(klayout -b -r "$KLAYOUT_SCRIPT" -rd input_parameter="${INPUT_PARAMETER}" 2>&1)"
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -ne 0 ]; then
  export KLAYOUT_STDOUT
  export KLAYOUT_EXIT_CODE="$EXIT_CODE"
  python3 - <<'PY'
import json, os
print(json.dumps({
    "ok": False,
    "error": f"KLayout exited with code {os.environ['KLAYOUT_EXIT_CODE']}",
    "stderr": os.environ["KLAYOUT_STDOUT"],
}, ensure_ascii=False))
PY
  exit "$EXIT_CODE"
fi

if [ -n "$CAPTURE_FILE" ]; then
  mkdir -p "$(dirname "$CAPTURE_FILE")"
  printf '%s\n' "$KLAYOUT_STDOUT" > "$CAPTURE_FILE"
fi

printf '%s\n' "$KLAYOUT_STDOUT"
```

---

## 🧠 二、Python 腳本標準範本（input_parameter.split(',') 版本）
```python
# klayout_task.py
import sys, json

def main(arg1, arg2, arg3):
    """
    概要：示範函式，接受三個位置參數。
    參數:
        arg1 (str): 第一個參數
        arg2 (str): 第二個參數
        arg3 (str): 第三個參數
    回傳: dict
    """
    # TODO: 實作你的邏輯
    result = {
        "ok": True,
        "arg1": arg1,
        "arg2": arg2,
        "arg3": arg3
    }
    return result

if __name__ == "__main__":
    raw = input_parameter  # KLayout -rd 傳入
    params = raw.split(",")
    if len(params) < 3:
        raise ValueError("需要三個以逗號分隔的參數：arg1,arg2,arg3")

    arg1, arg2, arg3 = [p.strip() for p in params[:3]]
    result = main(arg1, arg2, arg3)
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result.get("ok") else 1)
```

---

## 🧩 三、Python 腳本（JSON I/O 擴充範本）
> 用於支援新式 JSON 傳參，同時保留逗號 fallback。

```python
# klayout_json_io_template.py
import sys, json, os

def main(payload: dict) -> dict:
    """執行主要任務"""
    # TODO: 實作邏輯
    res = {
        "ok": True,
        "result": {"echo": payload},
    }
    if "out_json" in payload:
        with open(payload["out_json"], "w") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        res["written"] = payload["out_json"]
    return res

if __name__ == "__main__":
    raw = input_parameter  # KLayout 傳入
    try:
        payload = json.loads(raw)
    except Exception:
        # fallback: comma-separated string
        vals = [x.strip() for x in raw.split(",")]
        payload = {
            "in_gds": vals[0] if len(vals) > 1 else None,
        }

    result = main(payload)
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result.get("ok") else 1)
```

---

## 📄 四、JSON Input 與 Output 規範

### 🟢 JSON Input 格式
```json
{
  "task_id": "t01",
  "in_gds": "path/to.gds",
  "out_json": "result.json",
  "layer_filter": "1/0",
  "options": {
    "mode": "analyze",
    "flatten": true
  }
}
```

### 🔵 JSON Output 格式
**成功：**
```json
{
  "ok": true,
  "task_id": "t01",
  "result": {
    "num_polygons": 1250,
    "layers_found": ["1/0", "2/0"]
  },
  "written": "result.json"
}
```

**失敗：**
```json
{
  "ok": false,
  "error": "Missing input GDS file: path/to/gds"
}
```

---

## ⚙️ 五、Cline 執行規則
當 Cline 被指派修改或生成任何 KLayout 腳本時，必須遵守以下：

1. 所有入口腳本都必須使用：
   ```python
   if __name__ == "__main__":
       ...
   ```
2. 必須從 `input_parameter` 讀取輸入字串，並支援：
   - JSON 格式  
   - 逗號分隔格式（fallback）
3. 輸出必須是單一 `json.dumps(...)` 結果。
4. 結構中必須包含 `"ok": true/false`。
5. 若有寫檔行為，需包含 `"written": <path>`。
6. Shell wrapper 應傳入第一個引數為整串 JSON 或 CSV。
7. 任何偏離此規範的腳本，Cline 應主動標示「違規」並提出修正建議。

---

## 📋 六、實例命令示範
```bash
# JSON 參數傳遞
klayout -b -r src/adapters/klayout_py/c01_task.py   -rd input_parameter='{"task_id":"demo","in_gds":"a.gds","out_json":"out.json"}'

# CSV 傳遞（舊版 fallback）
klayout -b -r src/adapters/klayout_py/c01_task.py   -rd input_parameter="demo,a.gds,out.json"
```

---

## ✅ 七、規範總結
- 🧠 **輸入**：以 `input_parameter` 傳入 JSON 或逗號字串  
- 💾 **輸出**：統一 JSON 結構 `{ok:bool, error?:str, result?:any, written?:path}`  
- 🧱 **結構**：主函式 `main(payload:dict)` 或 `main(arg1,arg2,...)`  
- ⚙️ **行為**：`print(json.dumps(...))` 為唯一標準輸出  
- 🧩 **錯誤**：必須捕捉所有例外並以 JSON 格式回報  

---

> ✅ **Cline 提示**
> 
> 當生成klayout新腳本或修改現有腳本時：
> - 請明確遵守本規範；
> - 若規範被違反，請輸出「違規警告」並自動修正；
> - 將新增或修改的檔案註明「KLayout JSON I/O Compliant」。
