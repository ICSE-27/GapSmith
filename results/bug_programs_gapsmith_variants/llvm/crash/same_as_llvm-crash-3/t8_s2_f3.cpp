template <auto V>
struct ConstantWrapper {
  static constexpr auto value = V;

  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {
    return {};
  }
};

struct Sum3 {
  template <class T, class U, class V>
  constexpr auto operator()(T&& t, U&& u, V&& v) const -> decltype(static_cast<T&&>(t) + static_cast<U&&>(u) + static_cast<V&&>(v)) {
    return static_cast<T&&>(t) + static_cast<U&&>(u) + static_cast<V&&>(v);
  }
};

constexpr auto cwv = ConstantWrapper<Sum3{}>{}(ConstantWrapper<1>{}, ConstantWrapper<2>{}, ConstantWrapper<3>{});
