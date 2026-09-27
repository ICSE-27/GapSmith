template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
        template<typename... I>
        Type operator[](I...) { return {}; }
    };
    inner(Args...) -> inner<int>;
};
int main() {
    outer();
}
