template<typename T>
void foo() {
    static constexpr char string[] = "hello world";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            unsigned long sz { sizeof(string) };
        } s2;
    } object;
};
int main() { foo<void>(); }
