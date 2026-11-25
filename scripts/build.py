"""Build the static site: combine team data into data.json and inline it into public/index.html."""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "build_data.py"), ROOT], check=True)
html = open(os.path.join(ROOT, "src", "app.html")).read()
data = open(os.path.join(ROOT, "data.json")).read().replace("</", "<\\/")
os.makedirs(os.path.join(ROOT, "public"), exist_ok=True)
open(os.path.join(ROOT, "public", "index.html"), "w").write(html.replace("__DATA__", data, 1))
print("built public/index.html")
