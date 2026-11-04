#include <climits>
#include <new>

bool init(subvector *qv) {
    qv->mas = nullptr;
    qv->top = 0;
    qv->capacity = 0;
    return true;
}

bool resize(subvector *qv, unsigned int new_capacity) {
    if (new_capacity == qv->capacity) {
        return true;
    }

    if (new_capacity == 0) {
        delete[] qv->mas;
        qv->mas = nullptr;
        qv->top = 0;
        qv->capacity = 0;
        return true;
    }

    int *new_mas = new (std::nothrow) int[new_capacity];
    if (new_mas == nullptr) {
        return false;
    }

    unsigned int new_top = qv->top < new_capacity ? qv->top : new_capacity;
    for (unsigned int i = 0; i < new_top; ++i) {
        new_mas[i] = qv->mas[i];
    }

    delete[] qv->mas;
    qv->mas = new_mas;
    qv->top = new_top;
    qv->capacity = new_capacity;
    return true;
}

bool push_back(subvector *qv, int d) {
    if (qv->top == qv->capacity) {
        if (qv->capacity == UINT_MAX) {
            return false;
        }
        unsigned int new_capacity = qv->capacity == 0 ? 1
            : (qv->capacity > UINT_MAX / 2 ? UINT_MAX : qv->capacity * 2);
        if (!resize(qv, new_capacity)) {
            return false;
        }
    }
    qv->mas[qv->top++] = d;
    return true;
}

int pop_back(subvector *qv) {
    if (qv->top == 0) {
        return 0;
    }
    return qv->mas[--qv->top];
}

void shrink_to_fit(subvector *qv) {
    resize(qv, qv->top);
}

void clear(subvector *qv) {
    qv->top = 0;
}

void destructor(subvector *qv) {
    delete[] qv->mas;
    init(qv);
}

