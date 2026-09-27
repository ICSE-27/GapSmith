template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
        template<typename Self>
        void f(this Self&&) { }
    };
    inner(Args...) -> inner<int>;
};
int main() {
    outer();
}
