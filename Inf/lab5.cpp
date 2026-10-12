#include <iostream>
#include <fstream>
#include <cmath>
#include <chrono>
using namespace std;

const double PI = 3.14159265358979;
const long long MAXN = 100000000;

double get_time() {
    return std::chrono::duration_cast<std::chrono::microseconds>
        (std::chrono::steady_clock::now().time_since_epoch()).count() / 1e6;
}

long long wallis(double eps) {
    float p = 1;
    for (long long n = 1; n <= MAXN; n++) {
        float t = 4.0f * n * n;
        p *= t / (t - 1);
        if (fabs(2 * p - PI) < eps) return n;
    }
    return -1;
}

long long leibniz(double eps) {
    float s = 0, sign = 1;
    for (long long n = 1; n <= MAXN; n++) {
        s += sign / (2 * n - 1);
        sign = -sign;
        if (fabs(4 * s - PI) < eps) return n;
    }
    return -1;
}

long long basel(double eps) {
    float s = 0;
    for (long long n = 1; n <= MAXN; n++) {
        s += 1.0f / ((float)n * n);
        if (fabs(sqrt(6 * s) - PI) < eps) return n;
    }
    return -1;
}

long long nilakantha(double eps) {
    float s = 3, sign = 1;
    for (long long n = 1; n <= MAXN; n++) {
        float k = 2.0f * n;
        s += sign * 4 / (k * (k + 1) * (k + 2));
        sign = -sign;
        if (fabs(s - PI) < eps) return n;
    }
    return -1;
}

int main() {
    ofstream f("lab5.csv", ios::out);
    f << "formula,digits,iterations,time_us" << endl;

    string names[4] = {"wallis", "leibniz", "basel", "nilakantha"};
    long long (*formulas[4])(double) = {wallis, leibniz, basel, nilakantha};

    for (int i = 0; i < 4; i++) {
        double eps = 1;
        for (int digits = 1; digits <= 10; digits++) {
            eps /= 10;

            long long iters = formulas[i](eps);
            if (iters == -1) {
                cout << names[i] << ": " << digits << " digits - not reached" << endl;
                break;
            }

            int repeats = 0;
            double start = get_time();
            while (get_time() - start < 0.2) {
                formulas[i](eps);
                repeats++;
            }
            double time_us = (get_time() - start) / repeats * 1e6;

            f << names[i] << "," << digits << "," << iters << "," << time_us << endl;
            cout << names[i] << ": " << digits << " digits, " << iters
                 << " iterations, " << time_us << " us" << endl;
        }
    }
    return 0;
}
