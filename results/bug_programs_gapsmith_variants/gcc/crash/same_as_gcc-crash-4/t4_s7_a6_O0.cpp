template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            char* ptr { static_cast<char*>(::operator new(sizeof(string) * 2))};
            int extra { (int)sizeof(string) * 2 };
        } s2;
    } object;
};
int main() { foo<void>(); }
