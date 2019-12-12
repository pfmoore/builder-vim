from urllib.request import urlopen
import hashlib
import json
import io
import argparse
from zipfile import ZipFile
from pathlib import Path

def get_current_version(target):

    current = None
    if target.exists() and (target / "tag.txt").exists():
        current = (target / "tag.txt").read_text(encoding="utf-8").strip()

    return current

def get_new_release(current=None):
    PROJECT_URL = "https://api.github.com/repos/pfmoore/builder-vim/releases/latest"

    with urlopen(PROJECT_URL) as f:
        data = json.load(f)

    latest = data["name"]

    if current == latest:
        return None

    zip_name = f"vim-{latest}.zip"
    for asset in data["assets"]:
        if asset["name"] == zip_name:
            zip_url = asset["browser_download_url"]
        elif asset["name"] == zip_name + ".sha256":
            hash_url = asset["browser_download_url"]

    return (latest, zip_url, hash_url)

def extract(target, latest, zip_url, hash_url):
    # Download the zipfile and its hash
    with urlopen(zip_url) as f:
        print("Downloading zip data")
        zip_data = f.read()
    with urlopen(hash_url) as f:
        print("Downloading hash")
        hash_data = f.read().decode('ascii')

    # Check the hash matches
    h = hashlib.sha256()
    h.update(zip_data)
    if h.hexdigest() != hash_data:
        print(f"File {zip_url} has incorrect hash: {hash_data} vs {h.hexdigest()}")
        raise SystemExit

    # Extract the zipfile to the target directory
    with ZipFile(io.BytesIO(zip_data)) as z:
        print("Extracting files")
        z.extractall(target)

    # Record the package version
    (target / "tag.txt").write_text(latest, encoding="utf-8")

def ensure_target(target, current):
    if target.exists():
        suffix = current or "Old"
        target.rename(str(target) + "." + suffix)

    target.mkdir()

def parse_args():
    parser = argparse.ArgumentParser(description="Download the latest version of Vim")
    parser.add_argument("dest", help="Directory to extract the distribution to (e.g., C:\\Vim)")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    target = Path(args.dest)

    print(f"Installing to {target}...")
    current = get_current_version(target)
    print("Currently contains", f"version {current}" if current else "nothing")
    new = get_new_release(current)

    if not new:
        print(f"Skipping - no newer version than {current}")
        raise SystemExit

    latest, zip_url, hash_url = new

    if current:
        print(f"Upgrading from {current} to {latest}")
    else:
        print(f"Installing {latest}")

    ensure_target(target, current)

    extract(target, latest, zip_url, hash_url)
    print("Done")

if __name__ == "__main__":
    main()
