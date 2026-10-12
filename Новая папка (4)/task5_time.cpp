#include<iostream>
#include<cmath>
#include<fstream>
#include<chrono>
using namespace std;

bool prime_num(int x);
float fact(int x);
double get_time();
double average_time(int (*formula)(double), double acc);
const double PI = 3.1415926535;

int double_sum(double acc) 
{
    float res_pi = 0, sum = 0;

    for (int n = 1; n <= 10000; n++)
    {
        for (int m = 1; m <= n; m++)            
        {
            sum += 1.0f / (float)pow((4.0f * m - 2.0f), 2.0f * n);
        }
        for (int k = 1; k < n; k++)             
        {
            sum += 1.0f / (float)pow((4.0f * n - 2.0f), 2.0f * k);
        }

        res_pi = 8.0f * sum;
        if (abs(res_pi - PI) < acc)
        {
            return n;
        }
    }
    
    return -1;
}

int Ramanujan(double acc)
{
    float res_pi = 0, sum = 0, double_fact = 1;

    for (int k = 0; k < 100000000; k++)
    {
        if (k != 0)
        {
            double_fact *= (2.0f * k - 1.0f) / (2.0f * k);
        }

        sum += (float)pow(-1.0f, k) * (4.0f * k + 1.0f) * (float)pow(double_fact, 3.0f);
        res_pi = 2.0f / sum;
        if (abs(res_pi - PI) < acc)
        {
            return k + 1;
        }
    }

    return -1;
}

int Euler(double acc)
{
    float res_pi = 0, mult = 1;
    int k = 0;

    for (int p = 2; p <= 1000000; p++)
    {
        if (prime_num(p) == false)
        {
            continue;
        }

        mult *= ((float)p * (float)p) / ((float)p * (float)p - 1.0f);
        res_pi = sqrt(6.0f * mult);
        k++;
        if (abs(res_pi - PI) < acc)
        {
            return k;
        }
    }

    return -1;
}

int brothers_Chudnovsky(double acc)
{
    float res_pi = 0, sum = 0;

    for (int k  = 0; k < 10; k++)
    {
        sum += fact(6 * k) * (13591409 + 545140134.0f * k) 
               / (fact(3 * k) * (float)pow(fact(k), 3) * (float)pow(-640320, 3 * k));
        res_pi = 1.0f / (sum / (426880.0f * (float)sqrt(10005.0f)));
        if (abs(res_pi - PI) < acc)
        {
            return k + 1;
        }
    }

    return -1;
}

int main()
{
    ofstream f("task5_time.csv");

    for (int digits = 1; digits <= 10; digits++)
    {
        double acc = pow(10.0, -digits);
        int iters;

        iters = double_sum(acc);
        if (iters != -1)
        {
            int repeats = 100;
            auto start = get_time();
            for (int r = 0; r < repeats; r++)
            {
                double_sum(acc);
            }
            double t = (get_time() - start) / repeats * 1e9;
            f << "double_sum " << digits << " " << iters << " " << t << "\n";
        }

        iters = Ramanujan(acc);
        if (iters != -1)
        {
            int repeats = 3;
            auto start = get_time();
            for (int r = 0; r < repeats; r++)
            {
                Ramanujan(acc);
            }
            double t = (get_time() - start) / repeats * 1e9;
            f << "Ramanujan " << digits << " " << iters << " " << t << "\n";
        }

        iters = Euler(acc);
        if (iters != -1)
        {
            int repeats = 1000;
            auto start = get_time();
            for (int r = 0; r < repeats; r++)
            {
                Euler(acc);
            }
            double t = (get_time() - start) / repeats * 1e9;
            f << "Euler " << digits << " " << iters << " " << t << "\n";
        }

        iters = brothers_Chudnovsky(acc);
        if (iters != -1)
        {
            int repeats = 1000;
            double start = get_time();
            for (int r = 0; r < repeats; r++)
            {
                brothers_Chudnovsky(acc);
            }
            double t = (get_time() - start) / repeats * 1e9;
            f << "brother_Chudnovsky " << digits << " " << iters << " " << t << "\n";
        }

        cout << "10^-" << digits << " done" << endl;
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

double get_time()
{
    return std::chrono::duration_cast<std::chrono::microseconds>
        (std::chrono::steady_clock::now().time_since_epoch()).count() / 1e6;
}

