template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            int operator()(int x) requires (sizeof(string) > 1) { return x; }
        } s2;
    } object;
    (void)object.s2(1);
};
int main() { foo<void>(); }
