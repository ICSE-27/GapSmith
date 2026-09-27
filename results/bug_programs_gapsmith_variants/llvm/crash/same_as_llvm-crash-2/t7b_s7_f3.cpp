template<int& T> struct RefHolder { static int get() { return T; } };
template<int& T>
void FuncTemplate() {
    RefHolder<T> h; (void)h.get();
}

template<int i> class A {};
template<int i> void g(A<i> &) {
    static int InternalVar = 43;
    FuncTemplate<InternalVar>();
}

int main() {
  A<1> a;
  g(a);
}
