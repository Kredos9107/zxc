#include<iostream>
using namespace std;

void binary(unsigned int x);

union A
{
    unsigned int bit_i;
    float bit_f;
};

int main()
{
    cout << fixed;
    cout.precision(2);

    A x;
    long long x_true = 1;

    x.bit_f = 1;

    for (int i = 1; i <= 15; i++)
    {
        x.bit_f *= 10;
        x_true  *=  10;

        cout << "10^" << i << " | " << x.bit_f << " | ";
        binary(x.bit_i);
        cout << " | " << (long long)x.bit_f - x_true << endl;
    }

    return 0;
}

void binary(unsigned int x)
{
    const int MAX = 100;
    int k_zero = 0;
    bool flag = false;
    unsigned int mask = 1;
    
    int a[MAX];

    for (int i = 31; i >= 0; i--)
    {

        mask = 1 << (31 - i);

        if ((x & mask) != 0)
        {
            a[31 - i] = 1;
        }

        else
        {
            a[31 - i] = 0;
        }

    }

    for (int i = 31; i >= 0; i--)
    {
        if (a[i] == 0 && flag == false)
        {
            k_zero++;
            continue;
        }

        if (flag == false)
        {
            for (int j = 0; j < k_zero; j++)
            {
                cout << 0;
            }
        }

        flag = true;
        cout << a[i];
    }

    if (flag == false)
    {
        for (int j = 0; j < k_zero; j++)
        {
        cout << 0;
        }
    }
}
