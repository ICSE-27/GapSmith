template<typename T>
void foo() {
    static constexpr int arr[3] = {1,2,3};
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            void method() requires (arr[0] == 1) {}
        } s2;
    } object;
    object.s2.method();
};
int main() { foo<void>(); }
