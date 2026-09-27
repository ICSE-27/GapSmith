template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            char* ptr { static_cast<char*>(::operator new(alignof(char) + sizeof(string)))};
            int extra { (int)alignof(char) + sizeof(string) };
        } s2;
    } object;
};
int main() { foo<void>(); }
