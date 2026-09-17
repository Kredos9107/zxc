#include <iostream>
#include <algorithm>
using namespace std;

bool cmp(int a, int b) {
    return a > b;
}

int main() {
    int n;
    cin >> n;
    int pos[1000], neg[1000];
    int pc = 0, nc = 0;

    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        if (x >= 0) pos[pc++] = x;
        else neg[nc++] = x;
    }

    sort(pos, pos + pc);
    sort(neg, neg + nc, cmp);

    for (int i = 0; i < pc; i++) cout << pos[i] << " ";
    for (int i = 0; i < nc; i++) {
        cout << neg[i];
        if (i != nc - 1) cout << " ";
    }
}