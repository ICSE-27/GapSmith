template <class T>
struct Tester {
   struct Inner { using T2 = int; };
};
template <class T>
struct W { static Tester<T>::Inner::T2 m[2]; };
template <class T>
Tester<T>::Inner::T2 W<T>::m[2] = {1, 2};
template struct W<int>;
