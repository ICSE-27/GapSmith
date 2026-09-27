template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            char* ptr { static_cast<char*>(::operator new(sizeof(string)))};
        } s2;
        void method() noexcept(sizeof(string) > 0) {}
    } object;
};
int main() { foo<void>(); }
