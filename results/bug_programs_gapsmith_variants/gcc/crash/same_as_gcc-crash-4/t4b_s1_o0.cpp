template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            decltype(sizeof(string)) sz { sizeof(string) };
        } s2;
    } object;
};
int main() { foo<void>(); }
