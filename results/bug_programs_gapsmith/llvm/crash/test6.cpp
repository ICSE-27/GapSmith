template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   template <class U> using Alias = typename Inner::T2;
   static void test();
};

template <class T>
Tester<T>::Inner::T2 getInnerT2() { return {}; }

template <class T>
void Tester<T>::test() {
   auto _ = getInnerT2<T>();
}

template struct Tester<int>;
