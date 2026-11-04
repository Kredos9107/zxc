#include<iostream>
using namespace std;
int main()
{
    cout << fixed;
    cout.precision(2);

    for (float i = 16700000; i < 100000000; i++)
    {
        cout << i << "\n";
    }

    cout << "!";

    return 0;

}