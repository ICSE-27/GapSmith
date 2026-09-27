struct Base {
  virtual void doit(int) const;
  virtual int get();
  int val;
};
struct Mid : Base {};
struct Derived : Mid {
  void doit(int) const;
  int get();
};
typedef void (*free_t)(int);
void freefn(int);
typedef int (Base::*fn_t)();
struct help {
  fn_t ptr;
};
template <typename T=int> void generate() {
  constexpr help h{static_cast<fn_t>(&Derived::get)};
}
void f() { generate(); }
