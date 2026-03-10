import json
from datetime import datetime, timezone
from pathlib import Path

def utc():
    return datetime.now(timezone.utc).isoformat()

def write_json(path,data):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with open(path,"w") as f:
        json.dump(data,f,indent=2)

def append_jsonl(path,data):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with open(path,"a") as f:
        f.write(json.dumps(data)+"\n")

def load_json(path,default):
    if not Path(path).exists():
        return default
    with open(path) as f:
        return json.load(f)
