template<int& T, int& U>
void FuncTemplate() { (void)T; (void)U; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static int V1 = 43;
    static int V2 = 44;
    FuncTemplate<V1, V2>();
}

int main()
{
  A<1> a;
  g(a);
}
