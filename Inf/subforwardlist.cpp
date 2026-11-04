#include <new>

struct subforwardlist {
    int data;
    subforwardlist *next;
};

bool init(subforwardlist **sfl) {
    *sfl = nullptr;
    return true;
}

bool push_back(subforwardlist **sfl, int d) {
    subforwardlist *node = new (std::nothrow) subforwardlist{d, nullptr};
    if (node == nullptr) {
        return false;
    }

    while (*sfl != nullptr) {
        sfl = &(*sfl)->next;
    }
    *sfl = node;
    return true;
}

int pop_back(subforwardlist **sfl) {
    if (*sfl == nullptr) {
        return 0;
    }

    while ((*sfl)->next != nullptr) {
        sfl = &(*sfl)->next;
    }
    subforwardlist *last = *sfl;
    int result = last->data;
    *sfl = nullptr;
    delete last;
    return result;
}

bool push_forward(subforwardlist **sfl, int d) {
    subforwardlist *node = new (std::nothrow) subforwardlist{d, *sfl};
    if (node == nullptr) {
        return false;
    }
    *sfl = node;
    return true;
}

int pop_forward(subforwardlist **sfl) {
    if (*sfl == nullptr) {
        return 0;
    }

    subforwardlist *first = *sfl;
    int result = first->data;
    *sfl = first->next;
    delete first;
    return result;
}

bool push_where(subforwardlist **sfl, unsigned int where, int d) {
    for (unsigned int i = 0; i < where; ++i) {
        if (*sfl == nullptr) {
            return false;
        }
        sfl = &(*sfl)->next;
    }

    subforwardlist *node = new (std::nothrow) subforwardlist{d, *sfl};
    if (node == nullptr) {
        return false;
    }
    *sfl = node;
    return true;
}

int erase_where(subforwardlist **sfl, unsigned int where) {
    for (unsigned int i = 0; i < where; ++i) {
        if (*sfl == nullptr) {
            return 0;
        }
        sfl = &(*sfl)->next;
    }
    if (*sfl == nullptr) {
        return 0;
    }

    subforwardlist *node = *sfl;
    int result = node->data;
    *sfl = node->next;
    delete node;
    return result;
}

unsigned int size(subforwardlist **sfl) {
    unsigned int result = 0;
    for (subforwardlist *node = *sfl; node != nullptr; node = node->next) {
        ++result;
    }
    return result;
}

void clear(subforwardlist **sfl) {
    while (*sfl != nullptr) {
        subforwardlist *node = *sfl;
        *sfl = node->next;
        delete node;
    }
}
