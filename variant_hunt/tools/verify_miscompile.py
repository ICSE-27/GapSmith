#!/usr/bin/env python3
"""Re-verify MISCOMPILE hits with an independent reference compiler.

For each MISCOMPILE record: compile+run across ALL opt levels of the buggy
compiler AND a reference compiler (gcc13 for clang hits, clang-19.1.7 for gcc
hits). Keep only records where:
  - the buggy compiler diverges across its own opt levels, AND
  - some level disagrees with the reference compiler's agreed result
    (rules out UB / harness model bugs: if the reference also diverges,
     the program likely has UB -> discard as questionable).
Outputs results/verified_miscompiles.jsonl with a normalized true pattern.
"""
import json, os, subprocess, hashlib, sys, concurrent.futures as cf

ROOT = "/data/mingxuanzhu/GapSmith/variant_hunt"
RESDIR = os.path.join(ROOT, "results")
LEVELS = ["-O0", "-O1", "-O2", "-O3"]

CMDS = {
    "gcc":  ["/data/mingxuanzhu/gcc-14-build/gcc/xgcc", "-B", "/data/mingxuanzhu/gcc-14-build/gcc"],
    "gxx":  ["/data/mingxuanzhu/gcc-14-build/gcc/xg++", "-B", "/data/mingxuanzhu/gcc-14-build/gcc"],
    "clang":   ["/data/mingxuanzhu/llvm-build/bin/clang"],
    "clangxx": ["/data/mingxuanzhu/llvm-build/bin/clang++"],
}
REF = {
    "gcc": ["/data/mingxuanzhu/llvm-build/bin/clang"],       # clang 19.1.0 as referee for gcc C
    "gxx": ["/data/mingxuanzhu/llvm-build/bin/clang++"],
    "clang": ["gcc"],       # system gcc 13 for clang C
    "clangxx": ["g++"],
}

def run_one(cmd, flags, path, tag):
    exe = f"/tmp/vv_{os.getpid()}_{hashlib.md5((path+str(flags)+cmd[0]).encode()).hexdigest()[:8]}"
    extra = ["-std=c++20"] if tag == "gxx" else []
    c = subprocess.run(cmd + flags + [path, "-o", exe] + extra,
                       capture_output=True, text=True, timeout=90)
    if c.returncode != 0:
        return "CFAIL"
    try:
        r = subprocess.run([exe], capture_output=True, text=True, timeout=15)
        return f"exit={r.returncode}|{r.stdout.strip()[:60]}"
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    finally:
        subprocess.run(["rm", "-f", exe])

def verify(rec):
    path, tag = rec["file"], rec["tag"]
    if not os.path.exists(path):
        return None
    flags = [f for f in rec.get("flags", []) if not f.startswith("-O")]
    buggy = {o: run_one(CMDS[tag], flags + [o], path, tag) for o in LEVELS}
    reftag = "clangxx" if tag in ("clangxx", "gxx") else "clang"
    ref = {o: run_one(REF[tag], [o] + (["-std=c++20"] if tag in ("gxx",) else []), path, reftag) for o in LEVELS}
    buggy_div = len(set(buggy.values())) > 1
    ref_vals = set(ref.values())
    rec = dict(rec)
    rec["buggy_levels"] = buggy
    rec["ref_levels"] = ref
    if not buggy_div:
        rec["verdict"] = "no-repro-full-range"
    elif len(ref_vals) > 1:
        rec["verdict"] = "ref-also-diverges(UB?)"
    else:
        # which buggy levels disagree with the reference's agreed value
        refval = next(iter(ref_vals))
        bad = [o for o, v in buggy.items() if v != refval and v != "CFAIL"]
        rec["verdict"] = "CONFIRMED"
        rec["bad_levels"] = bad
        rec["ref_value"] = refval[:80]
    return rec

def main():
    hits = []
    for fn in sorted(os.listdir(RESDIR)):
        if not fn.endswith(".jsonl"):
            continue
        for line in open(os.path.join(RESDIR, fn)):
            r = json.loads(line)
            if r["status"] == "MISCOMPILE":
                r["campaign"] = fn[:-6]
                hits.append(r)
    print(f"re-verifying {len(hits)} miscompile hits...", flush=True)
    out = []
    with cf.ThreadPoolExecutor(max_workers=24) as ex:
        for i, res in enumerate(ex.map(verify, hits)):
            if res:
                out.append(res)
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(hits)}", flush=True)
    with open(os.path.join(RESDIR, "verified_miscompiles.jsonl"), "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    import collections
    c = collections.Counter(r["verdict"] for r in out)
    print(c)
    conf = [r for r in out if r["verdict"] == "CONFIRMED"]
    print(f"confirmed: {len(conf)}")

if __name__ == "__main__":
    main()
