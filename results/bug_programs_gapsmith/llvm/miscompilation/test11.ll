; LLVM 19.1.0 miscompilation case (IR level): i13 shift+mask equality folded to a
; rotate on x86-64 (llc -mtriple=x86_64-linux-gnu); wrong for a=2730 and a=5461.
define i64 @f(i64 %0) {
  %2 = lshr i64 %0, 8
  %3 = trunc i64 %2 to i13
  %4 = shl i13 %3, 2
  %5 = and i13 %3, -4
  %6 = icmp eq i13 %4, %5
  %7 = select i1 %6, i64 1, i64 3
  ret i64 %7
}
