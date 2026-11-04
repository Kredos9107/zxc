#include<iostream>
#include<cmath>
#include<fstream>
using namespace std;

bool prime_num(int x);
float fact(int x);

void double_sum(ofstream &f, int n)
{
    float res_pi = 0, sum = 0;

    for (int k = 1; k <= n; k++)
    {
        for (int m = 1; m <= n; m++)
        {
            sum += 1.0f / (float)pow((4.0f * m - 2.0f), 2.0f * k);
        }
    }

    res_pi = 8.0f * sum;
    f << "double_sum " << n << " " << res_pi << "\n";
}

void Ramanujan(ofstream &f, int n)
{
    float res_pi = 0, sum = 0, double_fact = 1;

    for (int k = 0; k < n; k++)
    {
        if (k != 0)
        {
            double_fact *= (2.0f * k - 1.0f) / (2.0f * k);
        }

        sum += (float)pow(-1.0f, k) * (4.0f * k + 1.0f) * (float)pow(double_fact, 3.0f);
    }

    res_pi = 2.0f / sum;
    f << "Ramanujan " << n << " " << res_pi << "\n";

}

void Euler(ofstream &f, int n)
{
    float res_pi = 0, mult = 1;

    for (int p = 2; p <= n; p++)
    {
        if (prime_num(p) == false)
        {
            continue;
        }

        mult *= ((float)p * (float)p) / ((float)p * (float)p - 1.0f);
    }

    res_pi = sqrt(6.0f * mult);
    f << "Euler " << n << " " << res_pi << "\n";
}

void brothers_Chudnovsky(ofstream &f, int n)
{
    float res_pi = 0, sum = 0;

    for (int k  = 0; k < n; k++)
    {
        sum += fact(6 * k) * (13591409 + 545140134.0f * k) 
               / (fact(3 * k) * (float)pow(fact(k), 3) * (float)pow(-640320, 3 * k));
    }

    sum = sum / (426880.0f * (float)sqrt(10005.0f));
    res_pi = 1.0f / sum;
    f << "brother_Chudnovsky " << n << " " << res_pi << "\n";
}

int main()
{
    ofstream f("task4_pi.csv");
    f << fixed;
    f.precision(10);

    for (int i = 1; i < 10000; i = i * 1.1 + 1)
    {
        double_sum(f, i);
    }

    for (int i = 1; i < 100000000; i = i * 1.1 + 1)
    {
        Ramanujan(f, i);
    }

    for (int i = 2; i < 1000000; i = i * 1.1 + 1)
    {
        Euler(f, i);
    }

    for (int i = 1; i < 10; i++)
    {
        brothers_Chudnovsky(f, i);
    }

    return 0;
}

bool prime_num(int x)
{
    if (x <= 1)
    {
        return false;
    }

    for (int i = 2; i * i <= x; i++)
    {
        if (x % i == 0)
        {
            return false;
        }
    }

    return true;
}

float fact(int x)
{
    float res = 1;

    for (int i = 2; i <= x; i++)
    {
        res *= i;
    }

    return res;
}
