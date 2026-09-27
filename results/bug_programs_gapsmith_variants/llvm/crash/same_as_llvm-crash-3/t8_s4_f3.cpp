template <auto V>
struct ConstantWrapper {
  static constexpr auto value = V;

  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {
    return {};
  }
};

struct Neg {
  template <class T>
  constexpr auto operator()(T&& t) const -> decltype(-static_cast<T&&>(t)) {
    return -static_cast<T&&>(t);
  }
};

constexpr auto cwv = ConstantWrapper<Neg{}>{}(ConstantWrapper<42>{});
