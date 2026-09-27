#!/usr/bin/env python3
"""UB / validity sweep over the packaged variant pool.

A. Miscompilation variants: build with system clang-19 (-fsanitize=undefined,
   -fno-sanitize-recover=all) at -O0 and run; any UBSan runtime error = UB found.
B. Crash variants: cross-compiler front-end acceptance as a program-validity
   proxy (g++ for clang-crash variants, clang for gcc-crash variants).
   GNU-C nested-function files are skipped (extension clang lacks).

Writes results/ubsan_sweep.jsonl and prints a summary.
"""
import json, os, subprocess, sys, concurrent.futures as cf, hashlib

ROOT = "/data/mingxuanzhu/GapSmith/results/bug_programs_gapsmith_variants"
RES = "/data/mingxuanzhu/GapSmith/variant_hunt/results"
CLANG = {".c": "/usr/bin/clang-19", ".cpp": "/usr/bin/clang++-19"}
GCCXX = "g++"

def ub_check(path):
    ext = os.path.splitext(path)[1]
    comp = CLANG.get(ext)
    if not comp:
        return None
    exe = f"/tmp/ub_{os.getpid()}_{hashlib.md5(path.encode()).hexdigest()[:8]}"
    std = ["-std=c23"] if ext == ".c" else ["-std=c++20"]
    c = subprocess.run([comp, "-fsanitize=undefined", "-fno-sanitize-recover=all",
                        "-O0"] + std + [path, "-o", exe],
                       capture_output=True, text=True, timeout=120)
    if c.returncode != 0:
        return {"file": path, "ub": None, "note": "compile-fail: " + (c.stderr or "")[:150]}
    try:
        r = subprocess.run([exe], capture_output=True, text=True, timeout=60)
        ub = "runtime error:" in (r.stderr or "") or "runtime error:" in (r.stdout or "")
        out = {"file": path, "ub": ub}
        if ub:
            out["detail"] = (r.stderr or r.stdout)[:300]
        return out
    except subprocess.TimeoutExpired:
        return {"file": path, "ub": None, "note": "run-timeout(60s)"}
    finally:
        subprocess.run(["rm", "-f", exe])

def cross_check(path):
    """front-end acceptance by the other compiler family"""
    ext = os.path.splitext(path)[1]
    if ext == ".c":
        src = open(path, errors="replace").read()
        if "asm volatile goto" in src or "asm goto" in src:
            comp, std = CLANG[".c"], ["-std=gnu17"]
        else:
            comp, std = CLANG[".c"], ["-std=c23"]
    else:
        comp, std = GCCXX, ["-std=c++23"]
    c = subprocess.run([comp, "-fsyntax-only"] + std + [path],
                       capture_output=True, text=True, timeout=60)
    ok = c.returncode == 0
    return {"file": path, "accepted": ok,
            "note": "" if ok else (c.stderr or "").strip().splitlines()[0][:150] if c.stderr else "rejected"}

def main():
    mis, crash = [], []
    for dirpath, _, files in os.walk(ROOT):
        for f in files:
            if not f.endswith((".c", ".cpp")):
                continue
            p = os.path.join(dirpath, f)
            if "/miscompilation/" in p:
                mis.append(p)
            elif "/crash/" in p:
                crash.append(p)
    print(f"miscompile variants: {len(mis)}, crash variants: {len(crash)}", flush=True)

    out_path = os.path.join(RES, "ubsan_sweep.jsonl")
    done = 0
    with open(out_path, "w") as out, cf.ThreadPoolExecutor(max_workers=32) as ex:
        for r in ex.map(ub_check, mis):
            r["kind"] = "ubsan"
            out.write(json.dumps(r) + "\n")
            done += 1
            if done % 50 == 0:
                print(f"  ubsan {done}/{len(mis)}", flush=True)
        done = 0
        for r in ex.map(cross_check, crash):
            r["kind"] = "cross-syntax"
            out.write(json.dumps(r) + "\n")
            done += 1
            if done % 200 == 0:
                print(f"  cross {done}/{len(crash)}", flush=True)
    print("wrote", out_path)
    # summary
    ub_found, ub_clean, ub_unknown = [], 0, []
    for l in open(out_path):
        r = json.loads(l)
        if r["kind"] != "ubsan":
            continue
        if r.get("ub") is True:
            ub_found.append(r)
        elif r.get("ub") is False:
            ub_clean += 1
        else:
            ub_unknown.append(r)
    print(f"UBSan: clean={ub_clean} UB-FOUND={len(ub_found)} unknown={len(ub_unknown)}")
    for r in ub_found[:10]:
        print("  UB:", r["file"], "|", r.get("detail", "")[:120])

if __name__ == "__main__":
    main()
