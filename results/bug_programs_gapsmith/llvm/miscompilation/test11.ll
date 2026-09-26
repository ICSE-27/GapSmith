; LLVM 19.1.0 miscompilation case (IR level): i3 shift+mask equality folded to a rotate
; on x86-64 (llc -mtriple=x86_64-linux-gnu); wrong for inputs a=2 and a=5.
define i64 @f(i64 %0) {
  %2 = lshr i64 %0, 8
  %3 = trunc i64 %2 to i3
  %4 = shl i3 %3, 2
  %5 = and i3 %3, -4
  %6 = icmp eq i3 %4, %5
  %7 = select i1 %6, i64 1, i64 3
  ret i64 %7
}
