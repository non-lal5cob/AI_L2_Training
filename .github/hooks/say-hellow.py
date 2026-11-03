import json
import sys

event = json.load(sys.stdin)
if isinstance(event, dict) and event.get("tool_name") == "Edit":
    print(json.dumps({"type": "progress", "message": "hello"}))
print("{}")