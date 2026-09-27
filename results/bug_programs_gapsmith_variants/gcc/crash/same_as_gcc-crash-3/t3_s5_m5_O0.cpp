struct Base {
  virtual void doit(int) const;
  virtual int get();
  int val;
};
struct Derived : Base {
  void doit(int) const;
  int get();
};
typedef void (*free_t)(int);
void freefn(int);
typedef void (Base::*fn_t)(int) const;
struct help {
  fn_t ptr;
};
template <typename T=int> void generate() {
  constexpr help h[2] = {{(fn_t)(&Derived::doit)}, {(fn_t)(&Derived::doit)}};
}
void f() { generate(); }
