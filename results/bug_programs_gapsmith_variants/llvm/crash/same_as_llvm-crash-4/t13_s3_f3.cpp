#include <coroutine>
template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
    };
    inner(Args...) -> inner<int>;
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
    outer();
    co_return;
}
int main() { bar(); }
