template<typename T>
void foo() {
    static constexpr unsigned arr[8] = {};
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            char* ptr { static_cast<char*>(::operator new(sizeof(arr)))};
        } s2;
    } object;
};
int main() { foo<void>(); }
