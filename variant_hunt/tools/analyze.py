#!/usr/bin/env python3
"""Analyze variant hunt results: cluster by bug key, mark which differ from seed.

Bug key normalization:
- GCC ICE: 'in <func>, at <file>:<line>' if present; else 'Segmentation fault' +
  top backtrace frames (func names only).
- LLVM CRASH: top non-runtime frames (func+file:line).
- MISCOMPILE: per-opt-level exit/output divergence pattern (levels + exit codes,
  not stdout text).
"""
import json, os, re, sys, collections

ROOT = "/data/mingxuanzhu/GapSmith/variant_hunt"
RESDIR = os.path.join(ROOT, "results")

BASELINE_KEYS = {
    "t1": "GCCSEGV:mark_addressable|build_addr",
    "t2": "GCCICE:build_conditional_expr:c/c-typeck.cc:5720",
    "t3": "GCCICE:fold_convert_loc:fold-const.cc:2757",
    "t4": "GCCICE:enclosing_instantiation_of:cp/pt.cc:15184",
    "t5": "MISCRASH:-O0=0,-O1=-11,-O2=-11",
    "t6": "LLVMSIG:DenseMapBase",           # getTypeInfoImpl
    "t7": "LLVMSIG:bare139",
    "t8": "LLVMSIG:ClassifyInternal(clang::ASTContext&, clang::Expr const*)@clang/lib/AST/ExprClassification.cpp:339:27",
    "t9": "LLVMSIG:clang::TreeTransform<(anonymous namespace)::TemplateInstantiator>::TransformType(clang::TypeLocBuilder&, clang::TypeLoc)",
    "t10": "MISCRASH:-O0=0,-O1=-11",
    "t11": "MISWRONG:-O0=0,-O1=2",
    "t12": "MISWRONG:-O1=0,-O2=1",
}

# signatures already discovered in waves 1-4 (packaged as new_*): a wave-5 hit
# with one of these keys is "known-new", not a fresh discovery.
KNOWN_NEW_KEYS = {
    "GCCICE:gimple_call_static_chain_flags:gimple.cc:1683",
    "GCCICE:build_conditional_expr:c/c-typeck.cc:5714",
    "LLVMSIG:HandleCrash@llvm/lib/Support/CrashRecoveryContext.cpp:71",
    "MISLINKFAIL:asm-goto-label",
    "MISCRASH:-O0=1,-O1=-11,-O2=-11",
    "MISWRONG:-O0=0,-O1=0,-O2=0",
}

def bug_key(rec):
    sig = rec["signature"]
    st = rec["status"]
    if st == "ICE":
        m = re.search(r"internal compiler error: in ([^,]+), at ([^ ]+)", sig)
        if m:
            return f"GCCICE:{m.group(1).strip()}:{m.group(2).strip()}"
        # segfault: frames after '::'
        frames = sig.split("::", 1)[1] if "::" in sig else ""
        funcs = [f.split("(")[0].strip() for f in frames.split("|") if f.strip()][:2]
        return "GCCSEGV:" + "|".join(funcs) if funcs else "GCCSEGV:noframes"
    if st == "CRASH":
        if "exit=139" in sig and ("::" not in sig or not sig.split("::", 1)[1].strip()):
            return "LLVMSIG:bare139"
        frames = sig.split("::", 1)[1] if "::" in sig else sig
        # keep func name + file:line of first frame
        first = frames.split("|")[0].strip()
        first = re.sub(r"\s+", " ", first)[:120]
        # shorten template noise
        if "DenseMapBase" in first:
            return "LLVMSIG:DenseMapBase"
        m = re.match(r"(.*?)(\S+\.(cpp|h|inc):\d+)", first)
        if m:
            return f"LLVMSIG:{m.group(1).strip()[-60:]}@{m.group(2)}"
        return "LLVMSIG:" + first[:80]
    if st == "SEGV":
        return "GCCSEGV:" + sig
    if st == "MISCOMPILE":
        # pattern: level:exitcode pairs only
        parts = re.findall(r"(-O\d| -Os|-Og):exit=(-?\d+)", sig)
        crash_levs = ",".join(f"{l}={e}" for l, e in sorted(parts))
        if any(e == "-11" for _, e in parts):
            return "MISCRASH:" + crash_levs
        return "MISWRONG:" + crash_levs
    return st

def main():
    clusters = collections.defaultdict(list)
    stats = collections.Counter()
    for fn in sorted(os.listdir(RESDIR)):
        if not fn.endswith(".jsonl"):
            continue
        campaign = fn[:-6]
        seed = campaign.split("_")[0]
        for line in open(os.path.join(RESDIR, fn)):
            rec = json.loads(line)
            rec["campaign"] = campaign
            rec["bug_key"] = bug_key(rec)
            stats[rec["status"]] += 1
            if rec["status"] in ("ICE", "CRASH", "SEGV", "MISCOMPILE"):
                clusters[(campaign, rec["bug_key"])].append(rec)

    print("== status counts ==")
    for st, n in stats.most_common():
        print(f"  {st}: {n}")
    print()
    print("== bug clusters (campaign, bug_key, count, differs-from-seed) ==")
    interesting = []
    for (campaign, key), recs in sorted(clusters.items()):
        seed = campaign.split("_")[0]
        baseline = BASELINE_KEYS.get(seed, "")
        diff = (key != baseline)
        # for miscompile keys, baseline prefix match
        if baseline.startswith("MIS") and key.startswith(baseline.split(":")[0]):
            diff = key != baseline
        marker = "DIFFERENT" if diff else "same-as-seed"
        if diff and key in KNOWN_NEW_KEYS:
            marker = "known-new(wave1-4)"
        elif diff:
            marker = "FRESH-NEW"
        print(f"  {campaign:22s} {key[:90]:92s} n={len(recs):4d}  {marker}")
        if diff and key not in KNOWN_NEW_KEYS:
            interesting.append((campaign, key, recs))
    print()
    print(f"total interesting clusters: {len(interesting)}")
    out = os.path.join(ROOT, "results", "interesting.json")
    with open(out, "w") as f:
        json.dump([{"campaign": c, "bug_key": k,
                    "count": len(r),
                    "examples": [{"name": x["name"], "file": x["file"],
                                  "flags": x["flags"], "signature": x["signature"]}
                                 for x in r[:5]]}
                   for c, k, r in interesting], f, indent=1)
    print("wrote", out)

if __name__ == "__main__":
    main()
