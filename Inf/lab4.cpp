#include <iostream>
#include <fstream>
#include <cmath>
using namespace std;

int main() {
    ofstream f("lab4.csv", ios::out);
    f << "formula,n,pi" << endl;
    f.precision(10);

    float leibniz = 0, wallis = 1, basel = 0, nilakantha = 3;
    float sign = 1;
    double next = 1;
    for (long long n = 1; n <= 100000000; n++) {
        leibniz += sign / (2 * n - 1);

        float t = 4.0f * n * n;
        wallis *= t / (t - 1);

        basel += 1.0f / ((float)n * n);

        float k = 2.0f * n;
        nilakantha += sign * 4 / (k * (k + 1) * (k + 2));

        sign = -sign;

        if (n >= next) {
            f << "leibniz," << n << "," << 4 * leibniz << endl;
            f << "wallis," << n << "," << 2 * wallis << endl;
            f << "basel," << n << "," << sqrt(6 * basel) << endl;
            f << "nilakantha," << n << "," << nilakantha << endl;
            next *= 1.1;
        }
    }
    return 0;
}
