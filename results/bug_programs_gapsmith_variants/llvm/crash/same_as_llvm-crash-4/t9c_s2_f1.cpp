template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        Type t;
        inner(Args...) { }
    };
    inner(Args...) -> inner<int>;
};
int main() {
    outer();
}
