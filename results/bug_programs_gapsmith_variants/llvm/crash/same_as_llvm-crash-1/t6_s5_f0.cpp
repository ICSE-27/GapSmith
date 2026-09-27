template <class T>
struct Tester {
   struct Inner {
      using T2 = int;
   };
};

template <class T>
Tester<T>::Inner::T2 getInnerT2() { return {}; }

int main() {
   auto x = getInnerT2<int>();
   (void)x;
}
