// Лаба по флоатам, пункт 1: float -> binary
// Компиляция: g++ task1.cpp -o task1
#include <iostream>
using namespace std;

// union: оба поля лежат в ОДНИХ И ТЕХ ЖЕ 4 байтах памяти.
// Записали число в .f, а прочитали те же биты через .u.
union fu {
    float f;
    unsigned int u;
};

// Пункт 0: печатает 32 бита unsigned int, начиная со старшего (левого).
void binary(unsigned int u) {
    for (int i = 31; i >= 0; i--) {
        // (u >> i) сдвигает i-й бит в самую правую позицию,
        // & 1 оставляет только его: получаем 0 или 1.
        cout << ((u >> i) & 1);
    }
    cout << endl;
}

// То же самое, но с пробелами между частями float:
// 1 бит знака | 8 бит порядка | 23 бита мантиссы.
void binary_float(unsigned int u) {
    for (int i = 31; i >= 0; i--) {
        cout << ((u >> i) & 1);
        if (i == 31 || i == 23) cout << ' ';
    }
    cout << endl;
}

int main() {
    fu a_lab_rat;
    cout.precision(12);  // печатать до 12 значащих цифр, чтобы увидеть неточность (по умолчанию 6)

    // Читаем числа, пока не закончится ввод (Ctrl+Z, Enter в Windows / Ctrl+D в Linux).
    while (cin >> a_lab_rat.f) {
        unsigned int u = a_lab_rat.u;

        cout << "float:  " << a_lab_rat.f << endl;
        cout << "bits:   ";
        binary(u);
        cout << "split:  ";
        binary_float(u);

        // Достаём три части побитовыми операциями.
        unsigned int sign = u >> 31;                // старший бит
        unsigned int exponent = (u >> 23) & 0xFF;   // 8 бит (0xFF = 11111111)
        unsigned int mantissa = u & 0x7FFFFF;       // младшие 23 бита (0x7FFFFF = 23 единицы)

        cout << "sign = " << sign
             << ", exponent = " << exponent << " (power = " << (int)exponent - 127 << ")"
             << ", mantissa = " << mantissa << endl;

        // Проверка IEEE 754 для нормальных чисел (exponent от 1 до 254):
        // value = (-1)^sign * 1.mantissa * 2^(exponent - 127)
        if (exponent != 0 && exponent != 255) {
            double value = 1.0 + mantissa / 8388608.0;   // 8388608 = 2^23, это "1.mantissa"
            int power = (int)exponent - 127;
            for (int i = 0; i < power; i++) value *= 2;  // без pow, как просят в лабе
            for (int i = 0; i > power; i--) value /= 2;
            if (sign == 1) value = -value;
            cout << "IEEE 754 check: " << value << endl;
        }
        cout << endl;
    }
    return 0;
}
