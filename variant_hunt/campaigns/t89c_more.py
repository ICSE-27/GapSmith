"""Campaign t8c/t9c: constant-wrapper and deduction-guide veins, new axes.
t8c: fold expressions, operator|, pointer args, CTAD, recursive instantiation.
t9c: constrained guides, requires on guide, copy-deduction, aggregates.
"""

T8 = [
    # fold over wrappers
    '''template <auto V>
struct ConstantWrapper {
  static constexpr auto value = V;
  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {
    return {};
  }
};
struct Plus {
  template <class T, class U>
  constexpr auto operator()(T&& t, U&& u) const -> decltype(static_cast<T&&>(t) + static_cast<U&&>(u)) {
    return static_cast<T&&>(t) + static_cast<U&&>(u);
  }
};
constexpr auto cwv = (ConstantWrapper<Plus{}>{}, ..., ConstantWrapper<42>{});''',
    # operator| chain
    '''template <auto V>
struct ConstantWrapper {
  static constexpr auto value = V;
  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {
    return {};
  }
};
struct Pipe {
  template <class T, class U>
  constexpr auto operator()(T&& t, U&& u) const -> decltype(static_cast<T&&>(t) | static_cast<U&&>(u)) {
    return static_cast<T&&>(t) | static_cast<U&&>(u);
  }
};
constexpr auto cwv = ConstantWrapper<Pipe{}>{}(ConstantWrapper<42>{}, ConstantWrapper<17>{});''',
    # pointer arithmetic functor
    '''template <auto V>
struct ConstantWrapper {
  static constexpr auto value = V;
  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {
    return {};
  }
};
struct PtrAdd {
  constexpr auto operator()(int const* p, int n) const -> int const* { return p + n; }
};
constexpr int arr[4] = {1,2,3,4};
constexpr auto cwv = ConstantWrapper<PtrAdd{}>{}(ConstantWrapper<&arr[0]>{}, ConstantWrapper<2>{});''',
    # CTAD of wrapper
    '''template <auto V>
struct ConstantWrapper {
  static constexpr auto value = V;
  ConstantWrapper() = default;
  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {
    return {};
  }
};
struct Plus {
  template <class T, class U>
  constexpr auto operator()(T&& t, U&& u) const -> decltype(static_cast<T&&>(t) + static_cast<U&&>(u)) {
    return static_cast<T&&>(t) + static_cast<U&&>(u);
  }
};
constexpr auto cwv = ConstantWrapper<Plus{}>{}.template operator()<ConstantWrapper<42>, ConstantWrapper<17>>({}, {});''',
    # lambda functor stored
    '''template <auto V>
struct ConstantWrapper {
  static constexpr auto value = V;
  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {
    return {};
  }
};
constexpr auto lam = []<class T, class U>(T t, U u) { return t + u; };
constexpr auto cwv = ConstantWrapper<lam>{}(ConstantWrapper<42>{}, ConstantWrapper<17>{});''',
]

T9 = [
    # constrained deduction guide
    '''template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
    };
    template <typename T = int> requires (sizeof...(Args) >= 0)
    inner(Args...) -> inner<T>;
};
int main() {
    outer();
}''',
    # copy deduction + pack
    '''template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
        inner(const inner&) { }
    };
    inner(Args...) -> inner<int>;
};
int main() {
    outer o;
    auto o2 = o;
    (void)o2;
}''',
    # aggregate with pack + guide
    '''template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        Type t;
        inner(Args...) { }
    };
    inner(Args...) -> inner<int>;
};
int main() {
    outer();
}''',
    # guide with trailing requires + decltype
    '''template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
    };
    inner(Args...) -> inner<decltype((Args{}, ...))>;
};
int main() {
    outer();
}''',
    # two packs interleaved
    '''template <typename... A1>
struct outer {
    template <typename Type, typename... A2>
    struct inner {
        inner(A1..., A2...) { }
    };
    template <typename... A2>
    inner(A1..., A2...) -> inner<int, A2...>;
};
int main() {
    outer();
}''',
]

FLAGS = [["-std=c++20"], ["-std=c++20", "-pedantic-errors"], ["-std=c++20", "-O2"], ["-std=c++17"], []]

def generate():
    for si, shape in enumerate(T8):
        src = shape + "\n"
        for fi, fl in enumerate(FLAGS):
            yield {"name": f"t8c_s{si}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
    for si, shape in enumerate(T9):
        src = shape + "\n"
        for fi, fl in enumerate(FLAGS):
            yield {"name": f"t9c_s{si}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
