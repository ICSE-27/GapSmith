template<typename T>
void foo() {
    static constexpr int arr[3] = {1,2,3};
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            char* ptr { static_cast<char*>(::operator new(sizeof(arr)))};
        } s2;
    } object;
};
int main() { foo<void>(); }
