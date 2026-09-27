template <typename... A1>
struct outer {
    template <typename Type, typename... A2>
    struct inner {
        inner(A1..., A2...) { }
    };
    template <typename... A2>
    inner(A1..., A2...) -> inner<int, A2...>;
};
int main() {
    outer();
}
