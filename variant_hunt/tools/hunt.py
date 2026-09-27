#!/usr/bin/env python3
"""Variant hunting driver.

Usage: hunt.py <campaign_module.py> [--limit N]

A campaign module defines generate() -> iterable of dicts:
  {name, src (source text), tag (gcc|gxx|clang|clangxx|llc),
   flags (list[str]), mode: 'compile' (default) | 'run',
   runflags: extra link flags for run mode,
   expect_run: dict describing expected runtime behavior (see run mode below)}

compile mode: classify.sh decides ICE/CRASH/ERROR/CLEAN/TIMEOUT.
run mode: compile (link) at each opt level in optlevels, run the binary,
  and flag MISCOMPILE when behavior differs between opt levels (or from
  expected), recording the differing outputs.

Results appended to results/<campaign>.jsonl with fields:
  name, status, signature, file (path to saved source), detail
Interesting = status in {ICE, CRASH, SEGV, MISCOMPILE} and
signature != baseline signature of the seed (checked later in analysis).
"""
import importlib.util, json, os, subprocess, sys, hashlib, concurrent.futures as cf

ROOT = "/data/mingxuanzhu/GapSmith/variant_hunt"
CLASSIFY = os.path.join(ROOT, "tools", "classify.sh")
VARDIR = os.path.join(ROOT, "variants")
RESDIR = os.path.join(ROOT, "results")

CMDS = {
    "gcc":  ["/data/mingxuanzhu/gcc-14-build/gcc/xgcc", "-B", "/data/mingxuanzhu/gcc-14-build/gcc"],
    "gxx":  ["/data/mingxuanzhu/gcc-14-build/gcc/xg++", "-B", "/data/mingxuanzhu/gcc-14-build/gcc"],
    "clang":   ["/data/mingxuanzhu/llvm-build/bin/clang"],
    "clangxx": ["/data/mingxuanzhu/llvm-build/bin/clang++"],
    "llc":     ["/data/mingxuanzhu/llvm-build/bin/llc"],
}

def save_src(campaign, name, src, ext):
    d = os.path.join(VARDIR, campaign)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name + ext)
    with open(p, "w") as f:
        f.write(src)
    return p

def run_compile(item, path):
    r = subprocess.run([CLASSIFY, path, item["tag"]] + item.get("flags", []),
                       capture_output=True, text=True, timeout=90)
    line = (r.stdout.strip().splitlines() or ["FAIL|no-output"])[0]
    status, _, sig = line.partition("|")
    return status, sig

def run_mode(item, path):
    """Compile+run at each opt level; compare behavior across levels."""
    levels = item.get("optlevels", ["-O0", "-O1", "-O2", "-O3"])
    outs = {}
    for o in levels:
        exe = f"/tmp/vh_run_{os.getpid()}_{hashlib.md5((item['name']+o).encode()).hexdigest()[:8]}"
        cmd = CMDS[item["tag"]] + item.get("flags", []) + [o, path, "-o", exe] + item.get("runflags", [])
        c = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        if c.returncode != 0:
            outs[o] = f"COMPILE_FAIL:{(c.stderr or '')[:120]}"
            continue
        try:
            r = subprocess.run([exe], capture_output=True, text=True, timeout=15)
            outs[o] = f"exit={r.returncode} out={r.stdout.strip()[:80]} err={r.stderr.strip()[:60]}"
        except subprocess.TimeoutExpired:
            outs[o] = "RUN_TIMEOUT"
        finally:
            subprocess.run(["rm", "-f", exe])
    distinct = set(outs.values())
    if len(distinct) > 1:
        # miscompile: behavior differs between opt levels
        sig = "; ".join(f"{k}:{v}" for k, v in sorted(outs.items()))[:400]
        return "MISCOMPILE", sig
    return "CLEAN", "; ".join(f"{k}:{v}" for k, v in sorted(outs.items()))[:200]

def process(campaign, item):
    ext = item.get("ext") or (".cpp" if item["tag"] in ("gxx", "clangxx") else ".c" if item["tag"] in ("gcc","clang") else ".ll")
    try:
        path = save_src(campaign, item["name"], item["src"], ext)
        if item.get("mode") == "run":
            status, sig = run_mode(item, path)
        else:
            status, sig = run_compile(item, path)
        return {"name": item["name"], "status": status, "signature": sig,
                "file": path, "flags": item.get("flags", []), "tag": item["tag"]}
    except Exception as e:
        return {"name": item["name"], "status": "HARNESS_FAIL", "signature": str(e)[:200]}

def main():
    mod_path = sys.argv[1]
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    campaign = os.path.splitext(os.path.basename(mod_path))[0]
    spec = importlib.util.spec_from_file_location(campaign, mod_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    items = list(mod.generate())
    if limit:
        items = items[:limit]
    os.makedirs(RESDIR, exist_ok=True)
    out = os.path.join(RESDIR, campaign + ".jsonl")
    n = 0
    with open(out, "w") as f, cf.ThreadPoolExecutor(max_workers=16) as ex:
        futs = [ex.submit(process, campaign, it) for it in items]
        for fut in cf.as_completed(futs):
            rec = fut.result()
            f.write(json.dumps(rec) + "\n")
            f.flush()
            n += 1
            if n % 50 == 0:
                print(f"[{campaign}] {n}/{len(items)}", flush=True)
    print(f"[{campaign}] done {n} -> {out}")

if __name__ == "__main__":
    main()
