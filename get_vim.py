from urllib.request import urlopen
import hashlib
import json
import io
from zipfile import ZipFile
from pathlib import Path

PROJECT_URL = "https://api.github.com/repos/pfmoore/builder-vim/releases/latest"
target = Path("Vim")
if not target.exists():
    target.mkdir()

current = None
if (target / "tag.txt").exists():
    current = (target / "tag.txt").read_text(encoding="utf-8")

with urlopen(PROJECT_URL) as f:
    data = json.load(f)

if data["name"] == current:
    print(f"Skipping - no newer version than {current}")
    raise SystemExit

zip_name = f"vim-{data['name']}.zip"
for asset in data["assets"]:
    if asset["name"] == zip_name:
        zip_url = asset["browser_download_url"]
    elif asset["name"] == zip_name + ".sha256":
        hash_url = asset["browser_download_url"]

with urlopen(zip_url) as f:
    zip_data = f.read()
with urlopen(hash_url) as f:
    hash_data = f.read().decode('ascii')

h = hashlib.sha256()
h.update(zip_data)
if h.hexdigest() != hash_data:
    print(f"File {zip_url} has incorrect hash: {hash_data} vs {h.hexdigest()}")
    raise SystemExit

with ZipFile(io.BytesIO(zip_data)) as z:
    z.extractall(target)
(target / "tag.txt").write_text(data["name"], encoding="utf-8")
