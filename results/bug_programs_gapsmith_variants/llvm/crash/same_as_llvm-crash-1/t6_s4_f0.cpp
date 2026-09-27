template <class T>
struct Tester {
   struct Inner {
      struct Innermost {
         using T3 = long;
      };
   };
   static void test();
};

template <class T>
Tester<T>::Inner::Innermost::T3 getT3() { return {}; }

template <class T>
void Tester<T>::test() {
   auto _ = getT3<T>();
}

template struct Tester<int>;
