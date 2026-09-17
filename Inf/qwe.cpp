#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    int n;
    cin >> n;
    int p[9999], o[9999];
    int pc = 0, nc = 0;

    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        if (x >= 0) {
            pc++;
            p[pc] = x;
        } else {
            nc++;
            o[nc] = x;
        }
    }

    sort(p, p + pc);
    sort(o, o + nc, greater<int>());

    for (int i = 0; i < pc; i++) cout << p[i] << " ";
    for (int i = 0; i < nc; i++) {
        cout << o[i];
        if (i != nc - 1) cout << " ";
    }
}