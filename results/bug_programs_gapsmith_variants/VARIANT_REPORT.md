# Variant hunt report — mutated bug programs with different bug reports

Date: 2026-09-27 (waves 1–7). Tooling: `variant_hunt/` (campaigns/, tools/classify.sh, hunt.py, analyze.py, verify_miscompile.py, package.py).
Compilers: GCC 14.3.0 (`/data/mingxuanzhu/gcc-14-build/gcc/{xgcc,xg++}`, --enable-checking=release) and
Clang 19.1.0 (`/data/mingxuanzhu/llvm-build/bin/{clang,clang++}`, assertions OFF) — the paper's versions.

## Method

Each of the 12 seed programs in `results/bug_programs_gapsmith/` was mutated along
semantic axes in 38 scripted campaigns (~38,000 variants total):

- waves 1–4: attribute kinds, types, control-flow shapes, template/constexpr forms,
  constants, opt flags;
- wave 5 (GCC-focused): -fexcess-precision, C++20 requires-clauses (found the
  mangler ICE), coroutines, register-output asm goto;
- wave 6 (LLVM-focused): wide `_BitInt` (33..120) legalization ops, C++20
  coroutines + template hybrids, C++23 deducing-this / static operator() /
  multidim subscript, OpenMP constructs, C `_Generic`/`_BitInt` front-end combos,
  SLP float/min-max/product reductions with `-mavx2`, t10-style structural fuzz;
- wave 7 (LLVM + cross-transfer): `__builtin_*` (clz/ctz/popcount/parity/overflow)
  on `_BitInt`, GCC-seed patterns retried on Clang and LLVM-seed patterns retried
  on GCC (cross-transfer), C++23 lambda-in-default-arg / multidim-subscript NTTP
  forms, and a 3,000-case random constant fuzz of the t10 seed.

Hits were clustered by normalized bug signature (ICE function+file:line +
backtrace frames for GCC, top crash frames for Clang, per-opt-level runtime
behavior for miscompiles). Miscompile hits were re-verified across `-O0..-O3`
against an independent reference compiler (clang for GCC hits, gcc-13 for Clang
hits; clang-19.1.7 for `_BitInt`).

## Result: 2,048 distinct variant programs trigger a bug

### A. New bug signatures — 713 variants (bug report differs from the seed)

| New signature dir | n | Compiler | What it is |
|---|---|---|---|
| `gcc/crash/new_gcc_ice_static_chain_flags` | 444 | GCC 14.3.0 | **ICE `gimple_call_static_chain_flags`, gimple.cc:1683** — `gcc_checking_assert(node->binds_to_current_def_p())` in the `ealias` (IPA mod-ref) pass. Trigger: three+ nested functions where a later one calls an earlier attribute-carrying one. Seed gcc-crash-1 was a segfault in tree-nested.cc lowering. Bugzilla: 0 hits (2026-09-27). |
| `gcc/crash/new_gcc_ice_cond_expr_op1` | 137 | GCC 14.3.0 | **ICE `build_conditional_expr`, c/c-typeck.cc:5714** — the operand-1 `gcc_assert` of the excess-precision ternary check (seed trips operand-2 at 5720, PR123370). Wave 5 added C++-mode, `_Complex`, decimal-float, `-fexcess-precision=*` variants. |
| `gcc/crash/new_gcc_ice_mangle_discriminator` | 37 | GCC 14.3.0 | **ICE `discriminator_for_local_entity`, cp/mangle.cc:2264** (wave 5) — `requires`/`noexcept` on a member of a nested local struct inside a template referencing `sizeof` of a function-local `static constexpr` array; every -O level, `-std=c++20`+. Same function as PR123529 (line 2316, RESOLVED) but a different surviving assertion. |
| `llvm/crash/new_llvm_crash_codegen_densemap` | 25 | Clang 19.1.0 | **Crash in CodeGen**, `DenseMap<const clang::Expr*, llvm::Value*>::moveFromOldBuckets`, when a function-local static is bound to a reference NTTP from inside a lambda (wave 1), a C++23 multidim-subscript operator template (wave 6), or a lambda in a template default argument (wave 7). Seed llvm-crash-2 crashes earlier in Sema (bare SIGSEGV). GitHub: no match (2026-09-27). |
| `gcc/miscompilation/new_gcc_asm_goto_crash_all_levels` | 18 | GCC 14.3.0 | Binary segfaults at **every** -O level including -O0 (seed: only -O1/-O2). Clang correct. |
| `gcc/miscompilation/new_gcc_asm_goto_silent_wrong_value` | 30 | GCC 14.3.0 | Silent wrong value from asm-goto `+m` outputs, value depends on -O level. Also on GCC 13.1 (longstanding). |
| `gcc/miscompilation/new_gcc_asm_goto_linkfail` | 30 | GCC 14.3.0 | Link failure `undefined reference to '.L3'` (two-label asm goto), all -O levels. Also on GCC 13.1. |

### B. Same-signature structural variants — 1,335 programs

| Dir | n | Seed (site) |
|---|---|---|
| `gcc/crash/same_as_gcc-crash-1` | 392 | nested-fn + attribute segfault (tree-nested.cc) |
| `gcc/crash/same_as_gcc-crash-2` | 357 | `_Float16` ternary ICE (c-typeck.cc:5720) |
| `gcc/crash/same_as_gcc-crash-3` | 72 | constexpr member-ptr ICE (fold-const.cc:2757) |
| `gcc/crash/same_as_gcc-crash-4` | 97 | local-static sizeof DMI ICE (pt.cc:15184) |
| `gcc/miscompilation/same_as_gcc-miscompilation-1` | 12 | asm-goto+TLS -O1/-O2 crash |
| `llvm/crash/same_as_llvm-crash-1` | 15 | missing-typename crash; wave 6 added deducing-this forms |
| `llvm/crash/same_as_llvm-crash-2` | 51 | local-static ref-NTTP segfault; wave 6 added subobject refs, deducing-this, multidim-subscript forms |
| `llvm/crash/same_as_llvm-crash-3` | 36 | constant-wrapper trailing-return crash; wave 6 added coroutine context |
| `llvm/crash/same_as_llvm-crash-4` | 74 | deduction-guide crash; wave 6 added C++23 static-lambda / deducing-this contexts |
| `llvm/miscompilation/same_as_llvm-miscompilation-1` | 42 | -O1-only runtime segfault |
| `llvm/miscompilation/same_as_llvm-miscompilation-2` | 86 | `_BitInt` shift/mask rotate fold (widths 3..30) |
| `llvm/miscompilation/same_as_llvm-miscompilation-3` | 93 | SLP narrowing (unsigned compare); waves 5–6 added -mavx2, `|`/`+`/`^` reductions, runtime-ref harnesses |

`variants_report.json` lists every file with its bug key, seed, and triggering flags.

## Validation

- Every packaged file reproduces from its delivered path (samples re-tested after
  each wave; final spot checks from the packaged tree).
- **UBSan sweep (tools/ubsan_sweep.py)**: every miscompilation variant was built
  with clang-19.1.7 `-fsanitize=undefined -fno-sanitize-recover=all -O0` and run:
  311 clean, 15 UB-found (all `t11b_w64_*` — a harness-side `1L<<64` loop-bound
  shift, not the rotate expression) → those 15 removed from the pool.
- **Crash-variant validity** (cross-compiler front-end acceptance as a proxy for
  program validity): `new_gcc_ice_mangle_discriminator` 37/37 and
  `new_llvm_crash_codegen_densemap` 25/25 are accepted cleanly by the other
  compiler (clang++-19 / g++-13) — ICE-on-valid. `same_as_gcc-crash-2` 357/357
  accepted; `new_gcc_ice_cond_expr_op1` 111/137 (26 use `_Float64x`-class types
  clang lacks on x86 — still GCC-valid). Nested-function variants
  (`new_gcc_ice_static_chain_flags`, `same_as_gcc-crash-1`) are GNU-C extensions
  clang rejects by design. `same_as_gcc-crash-3` / `same_as_llvm-crash-4` are
  rejected by the other compiler's stricter front end — those stand as
  crash-on-invalid robustness bugs (the compilers should diagnose, not crash).
- Current 12 seats: test2/test4 valid per clang, test6/test7/test8 valid per
  g++-13; test1 GNU-C extension; test3/test9 rejected by the stricter other
  front end (same as their seed programs' status).
- All miscompile hits re-verified against an independent compiler across -O0..-O3;
  reference-diverging (UB-suspect) records discarded.
- 7 flaky "crash" observations (t12b_92/145/601/712, t12c_1/2 + 1 ld artifact)
  did NOT reproduce in 20-run loops → discarded (blacklisted in package.py).
- t11 `_BitInt` rotate family also miscompiles identically on clang-19.1.7
  (confirms real wrong code, not UB).

## Negative results (axes explored, no divergence)

- **Wide/narrow `_BitInt` legalization**: div/mod/mul/add-wrap/xor-not/shift-W-1/
  boundary-compare at widths 33..120 (900 variants, UB-free construction
  verified) — all correct on Clang 19.1.0.
- `_BitInt` rotate-or / sub / xor / not / mul / add-wrap folds (t11c, 3,705
  variants) — only the shift-mask family folds wrongly.
- OpenMP constructs in templates (parallel-for/target/declare-reduction/task,
  128 compiles) — no crashes.
- C `_Generic`/switch/VLA/compound-literal/atomic combos with `_BitInt` (48).
- constexpr/consteval chains: virtual calls, dynamic_cast, placement new in
  templates (36) — no crashes.
- t10-style structural fuzz with nested loops / two switches / goto / recursion
  (2,592 variants) — no new divergence.
- GCC: register-output asm goto, nested-fn target_clones/ifunc attrs, dependent
  types in concepts/friends/partial specializations.
- `__builtin_clzg/ctzg/popcountg/parityg/add_overflow/sub_overflow` on `_BitInt`
  widths 3..64 (t18, 143 variants) — all correct.
- t10 random constant fuzz, 3,000 cases (t10d) — no divergence; the -O1 crash is
  highly structure-specific (wave-1 hits all share the seed's exact fallthrough
  chain).
- Cross-transfer (wave 7): Clang correctly *diagnoses* the GCC-FE crash patterns
  (missing typename, virtual-base member-ptr conversion) instead of crashing; GCC
  correctly diagnoses the LLVM-FE patterns and compiles `_BitInt` rotate / SLP
  cases correctly. No cross-compiler transfer hits.

## Caveats

- asm-goto silent-wrong-value and linkfail also reproduce on GCC 13.1 —
  longstanding issues, not new in 14.3.
- Tracker checks (2026-09-27): gimple.cc:1683 → Bugzilla 0 hits; c-typeck.cc:5714
  → only sibling PR123370 (line 5720); LLVM CodeGen DenseMap crash → no GitHub
  match; mangle.cc:2264 → same function as PR123529 (2316, RESOLVED) but a
  different surviving assertion. Novelty not guaranteed until triaged upstream.
