#include <iostream>
template<int& T>
void FuncTemplate() {
    std::cout << "ref: " << T << std::endl;
}

template<int i> class A {};
template<int i> void g(A<i> &) {
    static int InternalVar = 43;
    FuncTemplate<InternalVar>();
}

int main()
{
  A<1> a;
  g(a);
}
