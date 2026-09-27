template <auto V>
struct ConstantWrapper {
  static constexpr auto value = V;

  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {
    return {};
  }
};

struct Plus {
  template <class T, class U>
  constexpr auto operator()(T&& t, U&& u) const -> decltype(static_cast<T&&>(t) + static_cast<U&&>(u)) {
    return static_cast<T&&>(t) + static_cast<U&&>(u);
  }
};

constexpr auto cwv = ConstantWrapper<Plus{}>{}(ConstantWrapper<42>{}, ConstantWrapper<17>{});
