#!/usr/bin/env python3
"""Package verified variants into results/bug_programs_gapsmith_variants/.

Layout:
  <comp>/<category>/<signature-dir>/<variant>.c|cpp
  VARIANT_REPORT.md and variants_report.json at the root.

A variant = distinct SOURCE FILE that triggers a bug (dedup across opt flags;
flags that trigger are recorded). Signature dirs:
  new signature (differs from seed) -> 'new_<slug>'
  same signature as seed            -> 'same_as_<seed-id>'
"""
import json, os, re, shutil, collections, subprocess, sys

ROOT = "/data/mingxuanzhu/GapSmith/variant_hunt"
RES = os.path.join(ROOT, "results")
DEST = "/data/mingxuanzhu/GapSmith/results/bug_programs_gapsmith_variants"

SEEDS = {
    "t1": ("gcc", "crash", "gcc-crash-1", "GCCSEGV:mark_addressable|build_addr"),
    "t2": ("gcc", "crash", "gcc-crash-2", "GCCICE:build_conditional_expr:c/c-typeck.cc:5720"),
    "t3": ("gcc", "crash", "gcc-crash-3", "GCCICE:fold_convert_loc:fold-const.cc:2757"),
    "t4": ("gcc", "crash", "gcc-crash-4", "GCCICE:enclosing_instantiation_of:cp/pt.cc:15184"),
    "t5": ("gcc", "miscompilation", "gcc-miscompilation-1", "MISCRASH:-O0=0,-O1=-11,-O2=-11"),
    "t6": ("llvm", "crash", "llvm-crash-1", "LLVMSIG:DenseMapBase"),
    "t7": ("llvm", "crash", "llvm-crash-2", "LLVMSIG:bare139"),
    "t8": ("llvm", "crash", "llvm-crash-3",
           "LLVMSIG:ClassifyInternal(clang::ASTContext&, clang::Expr const*)@clang/lib/AST/ExprClassification.cpp:339:27"),
    "t9": ("llvm", "crash", "llvm-crash-4",
           "LLVMSIG:clang::TreeTransform<(anonymous namespace)::TemplateInstantiator>::TransformType(clang::TypeLocBuilder&, clang::TypeLoc)"),
    "t10": ("llvm", "miscompilation", "llvm-miscompilation-1", "MISCRASH:-O0=0,-O1=-11"),
    "t11": ("llvm", "miscompilation", "llvm-miscompilation-2", "MISWRONG:-O0=0,-O1=2"),
    "t12": ("llvm", "miscompilation", "llvm-miscompilation-3", "MISWRONG:-O1=0,-O2=1"),
}

NEW_SIG_INFO = {
    "GCCICE:gimple_call_static_chain_flags:gimple.cc:1683":
        ("new_gcc_ice_static_chain_flags", "gcc", "crash",
         "internal compiler error: in gimple_call_static_chain_flags, at gimple.cc:1683 "
         "(gcc_checking_assert(node->binds_to_current_def_p()) during the ealias/modref IPA pass). "
         "Different from the seed's segmentation fault in tree-nested.cc lowering."),
    "GCCICE:build_conditional_expr:c/c-typeck.cc:5714":
        ("new_gcc_ice_cond_expr_op1", "gcc", "crash",
         "internal compiler error: in build_conditional_expr, at c/c-typeck.cc:5714 "
         "(gcc_assert on operand 1 of the excess-precision conditional; the seed trips the operand-2 "
         "assertion at line 5720)."),
    "LLVMSIG:HandleCrash@llvm/lib/Support/CrashRecoveryContext.cpp:71":
        ("new_llvm_crash_codegen_densemap", "llvm", "crash",
         "Clang crashes inside CodeGen (DenseMap<const clang::Expr*, llvm::Value*>::moveFromOldBuckets) "
         "when a function-local static inside a lambda in a template is bound to a reference "
         "non-type template parameter. The seed crashes earlier, in Sema instantiation (bare SIGSEGV)."),
    "MISLINKFAIL:asm-goto-label":
        ("new_gcc_asm_goto_linkfail", "gcc", "miscompilation",
         "gcc emits an undefined-reference link error for a compiler-generated asm-goto label "
         "(.L3) at every optimization level; clang compiles and runs correctly. Also reproduces "
         "on GCC 13.1, so likely a longstanding asm-goto label-handling issue rather than a "
         "14.3 regression."),
    "MISCRASH:-O0=1,-O1=-11,-O2=-11":
        ("new_gcc_asm_goto_crash_all_levels", "gcc", "miscompilation",
         "Binary miscompiled so it crashes at every optimization level including -O0 "
         "(the seed only miscompiles at -O1/-O2). Verified against clang (correct)."),
    "MISWRONG:-O0=0,-O1=0,-O2=0":
        ("new_gcc_asm_goto_silent_wrong_value", "gcc", "miscompilation",
         "Silent wrong value (no crash): the abort-path return value differs between -O0/-O1 and "
         "-O2/-O3, and both disagree with clang. Also reproduces on GCC 13.1, so likely the known "
         "asm-goto output-operand issue family rather than a 14.3 regression."),
    "GCCICE:discriminator_for_local_entity:cp/mangle.cc:2264":
        ("new_gcc_ice_mangle_discriminator", "gcc", "crash",
         "internal compiler error: in discriminator_for_local_entity, at cp/mangle.cc:2264 — "
         "a requires-clause (or noexcept) on a member function of a nested local struct inside a "
         "template, referencing sizeof of a function-local static constexpr array, breaks name "
         "discrimination during mangling at C++20, at every -O level. Different file/function than "
         "the seed's cp/pt.cc instantiation-context failure."),
}

BLACKLIST = {"t12b_145", "t12b_601", "t12b_92", "t12b_712", "t12c_1", "t12c_2", "t12c_1", "t12c_2"}  # see also UB blacklist below

# UBSan-confirmed UB (t11b_w64: harness loop bound 1L<<64) — drop from pool
import os as _os
UB_BLACKLIST_PREFIX = "t11b_w64_"  # flaky/artifact, not reproducible

def bug_key(rec):
    sig = rec["signature"]
    st = rec["status"]
    if st == "ICE":
        m = re.search(r"internal compiler error: in ([^,]+), at ([^ ]+)", sig)
        if m:
            return f"GCCICE:{m.group(1).strip()}:{m.group(2).strip()}"
        frames = sig.split("::", 1)[1] if "::" in sig else ""
        funcs = [f.split("(")[0].strip() for f in frames.split("|") if f.strip()][:2]
        return "GCCSEGV:" + "|".join(funcs) if funcs else "GCCSEGV:noframes"
    if st == "CRASH":
        if "exit=139" in sig and ("::" not in sig or not sig.split("::", 1)[1].strip()):
            return "LLVMSIG:bare139"
        frames = sig.split("::", 1)[1] if "::" in sig else sig
        first = frames.split("|")[0].strip()
        if "DenseMapBase" in first and "TypeInfo" in first:
            return "LLVMSIG:DenseMapBase"
        if "HandleCrash" in first:
            return "LLVMSIG:HandleCrash@llvm/lib/Support/CrashRecoveryContext.cpp:71"
        if "ClassifyInternal" in first:
            return "LLVMSIG:ClassifyInternal(clang::ASTContext&, clang::Expr const*)@clang/lib/AST/ExprClassification.cpp:339:27"
        if "TreeTransform" in first:
            return "LLVMSIG:clang::TreeTransform<(anonymous namespace)::TemplateInstantiator>::TransformType(clang::TypeLocBuilder&, clang::TypeLoc)"
        return "LLVMSIG:" + first[:80]
    if st == "MISCOMPILE":
        if "RUN_TIMEOUT" in sig or "COMPILE_FAIL" in sig:
            # distinguish link-time label failure (real distinct manifestation)
            if "undefined reference to" in sig and ".L" in sig:
                return "MISLINKFAIL:asm-goto-label"
            return "INVALID:timeout-or-cfail"
        parts = re.findall(r"(-O\d| -Os|-Og):exit=(-?\d+)", sig)
        crash_levs = ",".join(f"{l}={e}" for l, e in sorted(parts))
        if any(e == "-11" for _, e in parts):
            return "MISCRASH:" + crash_levs
        return "MISWRONG:" + crash_levs
    return st

def collect():
    """group distinct source files by (seed, bug_key) with trigger flags"""
    groups = collections.defaultdict(lambda: {"flags": set(), "names": [], "src": None, "tag": None})
    skip = {"verified_miscompiles", "ubsan_sweep"}
    for fn in sorted(os.listdir(RES)):
        if not fn.endswith(".jsonl") or fn[:-6] in skip:
            continue
        campaign = fn[:-6]
        m = re.match(r"(t\d+)", campaign)
        seed = m.group(1) if (m and m.group(1) in SEEDS) else None
        if seed is None and campaign.startswith("t89"):
            seed = None  # mixed t8/t9 campaign: per-record attribution below
        for line in open(os.path.join(RES, fn)):
            r = json.loads(line)
            if r["status"] not in ("ICE", "CRASH", "SEGV", "MISCOMPILE"):
                continue
            key = bug_key(r)
            # normalize miscompile families: wrong-count magnitude and inverted
            # screening labels from a broken expected-model are the same bug
            # report as the seed (verified: bad levels are -O2/-O3 for t12).
            if key.startswith("MISWRONG") and campaign in ("t11_bitint", "t11b_widths", "t11c_bitops"):
                key = "MISWRONG:-O0=0,-O1=2"          # rotate-fold family
            if key.startswith("MISWRONG") and campaign in ("t12_slp", "t12b_slp2", "t12c_slp3"):
                key = "MISWRONG:-O1=0,-O2=1"          # SLP-narrowing family
            if key == "INVALID:timeout-or-cfail":
                continue
            if r["name"] in BLACKLIST:
                continue
            if r["name"].startswith(UB_BLACKLIST_PREFIX):
                continue  # UBSan: harness UB (1L<<64 loop bound), not a valid bug
            rseed = seed
            if rseed is None:
                # hybrid/mixed campaigns: attribute to the seed whose baseline
                # key matches, else bucket by name prefix (t8c -> t8, t9c -> t9)
                for s, (_, _, _, skey) in SEEDS.items():
                    if key == skey:
                        rseed = s
                        break
                else:
                    if campaign.startswith("t8") or r["name"].startswith("t8c"):
                        rseed = "t8"
                    elif campaign.startswith("t9") or r["name"].startswith("t9c"):
                        rseed = "t9"
                    else:
                        rseed = "t7"
            fpath = r["file"]
            g = groups[(rseed, key, fpath)]
            g["names"].append(r["name"])
            g["flags"].add(tuple(r.get("flags", [])))
            g["src"] = fpath
            g["tag"] = r["tag"]
            g["campaign"] = campaign
    return groups

def main():
    groups = collect()
    if os.path.exists(DEST):
        keep = os.path.join(DEST, "VARIANT_REPORT.md")
        saved = open(keep).read() if os.path.exists(keep) else None
        shutil.rmtree(DEST)
        if saved is not None:
            os.makedirs(DEST, exist_ok=True)
            open(keep, "w").write(saved)
    report = {"new_signatures": collections.defaultdict(list),
              "same_signature": collections.defaultdict(list)}
    counts = collections.Counter()
    for (seed, key, fpath), g in sorted(groups.items()):
        if seed in SEEDS:
            comp, cat, seed_id, seed_key = SEEDS[seed]
        else:
            comp, cat, seed_id, seed_key = ("llvm", "crash", "llvm-hybrid", "\0")
        same = (key == seed_key)
        if not same and key in NEW_SIG_INFO:
            dirname, comp2, cat2, desc = NEW_SIG_INFO[key]
            sub = dirname
        elif not same and key.startswith("MIS"):
            # miscompile pattern differs from seed
            sub = f"new_pattern_{re.sub(r'[^A-Za-z0-9]+','_',key)[:60]}"
        elif not same:
            sub = f"new_sig_{re.sub(r'[^A-Za-z0-9]+','_',key)[:60]}"
        else:
            sub = f"same_as_{seed_id}"
        outdir = os.path.join(DEST, comp, cat, sub)
        os.makedirs(outdir, exist_ok=True)
        base = os.path.basename(fpath)
        dst = os.path.join(outdir, base)
        # avoid collisions
        if os.path.exists(dst):
            dst = os.path.join(outdir, g["campaign"] + "__" + base)
        shutil.copy2(fpath, dst)
        entry = {
            "variant": os.path.relpath(dst, DEST),
            "seed": seed_id,
            "bug_key": key,
            "same_signature_as_seed": same,
            "trigger_flags": sorted("+".join(f) for f in g["flags"]),
            "source_campaign": g["campaign"],
        }
        bucket = "same_signature" if same else "new_signatures"
        report[bucket][sub].append(entry)
        counts[(bucket, sub)] += 1
    # summary
    print("== packaged ==")
    for (bucket, sub), n in sorted(counts.items()):
        print(f"  {bucket:16s} {sub:55s} {n}")
    with open(os.path.join(DEST, "variants_report.json"), "w") as f:
        json.dump({
            "new_signatures": {k: v for k, v in sorted(report["new_signatures"].items())},
            "same_signature": {k: v for k, v in sorted(report["same_signature"].items())},
        }, f, indent=1)
    print("total distinct source files:",
          sum(counts.values()))

if __name__ == "__main__":
    main()
