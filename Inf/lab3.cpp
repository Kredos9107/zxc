#include <iostream>
using namespace std;

int main() {
    cout << fixed;
    cout.precision(2);

    long long steps = 0;
    for (float x = 0; x < 100000000; x += 1) {
        steps++;
        if (steps % 10000000 == 0)
            cout << "steps: " << steps << "  x = " << x << endl;
    }
    return 0;
}
