#include <new>

struct subset_node {
    int key;
    subset_node *left;
    subset_node *right;
};

bool init(subset_node **sn) {
    *sn = nullptr;
    return true;
}

bool insert(subset_node **sn, int k) {
    while (*sn != nullptr) {
        if (k < (*sn)->key) sn = &(*sn)->left;
        else if (k > (*sn)->key) sn = &(*sn)->right;
        else return false;
    }
    *sn = new (std::nothrow) subset_node{k, nullptr, nullptr};
    return *sn != nullptr;
}

bool remove(subset_node **sn, int k) {
    while (*sn != nullptr && (*sn)->key != k) {
        if (k < (*sn)->key) sn = &(*sn)->left;
        else sn = &(*sn)->right;
    }
    if (*sn == nullptr) return false;

    subset_node *node = *sn;
    if (node->left != nullptr && node->right != nullptr) {
        subset_node **next = &node->right;
        while ((*next)->left != nullptr) next = &(*next)->left;
        node->key = (*next)->key;
        subset_node *old = *next;
        *next = old->right;
        delete old;
    } else {
        *sn = node->left != nullptr ? node->left : node->right;
        delete node;
    }
    return true;
}

subset_node *find(subset_node *sn, int k) {
    while (sn != nullptr) {
        if (k < sn->key) sn = sn->left;
        else if (k > sn->key) sn = sn->right;
        else return sn;
    }
    return nullptr;
}

unsigned int size(subset_node *sn) {
    if (sn == nullptr) return 0;
    return 1 + size(sn->left) + size(sn->right);
}

unsigned int height(subset_node *sn) {
    if (sn == nullptr || (sn->left == nullptr && sn->right == nullptr)) return 0;
    unsigned int left = height(sn->left);
    unsigned int right = height(sn->right);
    return 1 + (left > right ? left : right);
}

void clear_tree(subset_node *sn) {
    if (sn == nullptr) return;
    clear_tree(sn->left);
    clear_tree(sn->right);
    delete sn;
}

void destructor(subset_node **sn) {
    clear_tree(*sn);
    *sn = nullptr;
}

void destructor(subset_node *sn) {
    clear_tree(sn);
}

void dfs_fill(subset_node *sn, int *result, unsigned int &pos) {
    if (sn == nullptr) return;
    dfs_fill(sn->left, result, pos);
    result[pos++] = sn->key;
    dfs_fill(sn->right, result, pos);
}

int *DFS(subset_node *sn) {
    int *result = new (std::nothrow) int[size(sn)];
    if (result == nullptr) return nullptr;
    unsigned int pos = 0;
    dfs_fill(sn, result, pos);
    return result;
}

