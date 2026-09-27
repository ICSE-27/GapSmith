#include <coroutine>
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
struct task {
  struct promise_type {
    task get_return_object() { return {}; }
    std::suspend_never initial_suspend() { return {}; }
    std::suspend_never final_suspend() noexcept { return {}; }
    void return_void() {}
    void unhandled_exception() {}
  };
};
task bar() {
    constexpr auto cwv = ConstantWrapper<Plus{}>{}(ConstantWrapper<42>{}, ConstantWrapper<17>{});
    co_return;
}
int main() { bar(); }
