template <class T>
struct Tester {
   struct Inner { using T2 = int; };
};
template <class T>
struct W { static Tester<T>::Inner::T2 m; };
template <class T>
Tester<T>::Inner::T2 W<T>::m = 0;
template <class U> void use() { (void)W<U>::m; }
template void use<int>();
