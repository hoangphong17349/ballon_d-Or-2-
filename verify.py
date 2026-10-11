#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify every year has a page, index links all of them, no broken paths."""

import os, re, zipfile

BASE = "/home/user/proj"
os.chdir(BASE)

idx = open("index.html", encoding="utf-8").read()
links = re.findall(r'href="(ballon-dor-(\d{4})\.html)"', idx)
missing = [f for f, y in links if not os.path.isfile(f)]
years_linked = sorted(int(y) for _, y in links)
pages = sorted(
    int(re.search(r"(\d{4})", f).group(1))
    for f in os.listdir(".")
    if re.match(r"ballon-dor-\d{4}\.html$", f)
)
print("index link count      :", len(links))
print("broken links          :", missing)
print("distinct years linked :", len(set(years_linked)))
print("years in index        :", min(years_linked), "->", max(years_linked))
print("year page files       :", len(pages), "|", min(pages), "->", max(pages))
print("pages not linked      :", sorted(set(pages) - set(years_linked)))
print("links without a page  :", sorted(set(years_linked) - set(pages)))

# internal hrefs on every page must resolve
bad = []
for f in sorted(os.listdir(".")):
    if not re.match(r"ballon-dor-\d{4}\.html$", f):
        continue
    s = open(f, encoding="utf-8").read()
    for href in re.findall(r'href="([^"#]+?)"', s):
        if href.startswith(("http", "mailto")):
            continue
        if not os.path.isfile(href):
            bad.append((f, href))
print("unresolved internal hrefs:", bad)

# prev/next chain sanity: 1956 -> 2025 should be reachable
start, seen, chain = 1956, set(), []
while True:
    chain.append(start)
    s = open(f"ballon-dor-{start}.html", encoding="utf-8").read()
    m = re.search(
        r'<nav class="pager">.*?<a href="ballon-dor-(\d{4})\.html">(\d{4})</a>\s*</nav>',
        s,
    )
    if not m:
        break
    nxt = int(m.group(1))
    if nxt in seen:
        break
    seen.add(nxt)
    start = nxt
print("forward chain        :", chain[0], "->", chain[-1], f"({len(chain)} steps)")

os.makedirs("dist", exist_ok=True)
zpath = "dist/ballon-dor-project.zip"
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(".")):
        if f in ("gen.py", "rankings.txt", "dist") or f.startswith("preview-"):
            continue
        z.write(f)
print(
    "zip:",
    zpath,
    round(os.path.getsize(zpath) / 1024, 1),
    "KB",
    "|",
    len(zipfile.ZipFile(zpath).namelist()),
    "files",
)
