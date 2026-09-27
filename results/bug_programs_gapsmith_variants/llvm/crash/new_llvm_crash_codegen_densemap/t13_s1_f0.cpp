#include <coroutine>
template<int& T> void FuncTemplate() { (void)T; }
struct task {
  struct promise_type {
    task get_return_object() { return {}; }
    std::suspend_never initial_suspend() { return {}; }
    std::suspend_never final_suspend() noexcept { return {}; }
    void return_void() {}
    void unhandled_exception() {}
  };
};
template<typename T>
task foo() {
    [](){ static int InternalVar = 43; FuncTemplate<InternalVar>(); }();
    co_return;
}
int main() { foo<int>(); }
