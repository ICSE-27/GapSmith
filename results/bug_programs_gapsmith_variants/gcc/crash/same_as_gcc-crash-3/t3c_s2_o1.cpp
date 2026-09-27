struct Base { virtual void doit(int) const; virtual void other(int) const; int val; };
struct Derived : Base { void doit(int) const; void other(int) const; };
typedef void (Base::*fn_t)(int) const;
struct help {
  fn_t ptrs[2];
};
template <typename T=int> void generate() {
  constexpr help h{{static_cast<fn_t>(&Derived::doit), static_cast<fn_t>(&Derived::other)}};
}
void f() { generate(); }
