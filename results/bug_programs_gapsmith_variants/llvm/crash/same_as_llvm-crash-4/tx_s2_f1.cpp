template <auto V>
struct ConstantWrapper {
  static constexpr auto value = V;
  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {
    return {};
  }
};
template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
        ConstantWrapper<sizeof...(Args)> cw;
    };
    inner(Args...) -> inner<int>;
};
int main() {
    outer();
}
