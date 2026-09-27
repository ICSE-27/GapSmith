#!/usr/bin/env bash
# classify.sh <file> <compiler-tag> <flags...>
set -u
F=$1; TAG=$2; shift 2
GCCDIR=/data/mingxuanzhu/gcc-14-build/gcc
case $TAG in
  gcc)  CMD="/data/mingxuanzhu/gcc-14-build/gcc/xgcc -B $GCCDIR";;
  gxx)  CMD="/data/mingxuanzhu/gcc-14-build/gcc/xg++ -B $GCCDIR";;
  clang) CMD="/data/mingxuanzhu/llvm-build/bin/clang";;
  clangxx) CMD="/data/mingxuanzhu/llvm-build/bin/clang++";;
  llc) CMD="/data/mingxuanzhu/llvm-build/bin/llc";;
esac
LOG=$(mktemp)
timeout 60 $CMD "$@" -c "$F" -o /tmp/vh_out_$$.o >"$LOG" 2>&1
E=$?
if [ $E -eq 124 ]; then echo "TIMEOUT|"; rm -f "$LOG" /tmp/vh_out_$$.o; exit 0; fi
ICE=$(grep -m1 -E "internal compiler error" "$LOG" | sed "s|$F:||" || true)
if [ -n "$ICE" ]; then
  # append distinctive backtrace frames (skip crash_signal/???/libc)
  BT=$(grep -E "^0x[0-9a-f]+ " "$LOG" | grep -vE "crash_signal|\?\?\?|libc_sigaction" | head -2 | sed 's/^0x[0-9a-f]* *//' | tr '\n' '|' | head -c 240)
  echo "ICE|$ICE :: $BT"
  rm -f "$LOG" /tmp/vh_out_$$.o; exit 0
fi
if grep -qE "PLEASE submit a bug report|Stack dump|Segmentation fault" "$LOG" || [ $E -ge 128 ]; then
  SIG=$(grep -E "^#[0-9]+ " "$LOG" | grep -vE "PrintStackTrace|SignalHandler|sys::|_L|pthread|raise|abort|libc|kill" | head -2 | sed 's/0x[0-9a-f]*//g;s/^ *#[0-9]* *//;s|/data/mingxuanzhu/llvm-project/||' | tr '\n' '|' | head -c 300)
  echo "CRASH|exit=$E :: $SIG"
  rm -f "$LOG" /tmp/vh_out_$$.o; exit 0
fi
ERR=$(grep -m1 -E "error:" "$LOG" | sed "s|$F:||" || true)
if [ -n "$ERR" ]; then echo "ERROR|$ERR"; rm -f "$LOG" /tmp/vh_out_$$.o; exit 0; fi
if [ $E -ne 0 ]; then echo "FAIL|exit=$E $(head -c 150 "$LOG" | tr '\n' ' ')"; rm -f "$LOG" /tmp/vh_out_$$.o; exit 0; fi
echo "CLEAN|"
rm -f "$LOG" /tmp/vh_out_$$.o
