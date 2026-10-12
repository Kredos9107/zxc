#include <iostream>
using namespace std;

union fu {
    float f;
    unsigned int u;
};

void binary(unsigned int u) {
    for (int i = 31; i >= 0; i--)
        cout << ((u >> i) & 1);
    cout << endl;
}

int main() {
    cout << fixed;
    cout.precision(2);

    fu x;
    x.f = 1.0;
    for (int i = 1; i <= 15; i++) {
        x.f *= 10;
        cout << x.f << "  ";
        binary(x.u);
    }
    return 0;
}
