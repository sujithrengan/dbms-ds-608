#include <iostream>
#include <vector>
using namespace std;

class BPlusTreeNode
{
public:
    vector<int> keys;
    vector<BPlusTreeNode*> children;
    BPlusTreeNode* parent;
    BPlusTreeNode* next;
    BPlusTreeNode* prev;
    bool is_leaf;
    int order;

    BPlusTreeNode(int order, bool is_leaf){
        this->order = order;
        this->is_leaf = is_leaf;
        this->parent = NULL;
        this->next = NULL;
        this->prev = NULL;
        this->keys.resize(order);
        this->children.resize(order+1);
    }
};

class BPlusTree
{
public:
    BPlusTree(int order){
        this->order = order;
        this->root = new BPlusTreeNode(order, true);
    }
    
private:
    BPlusTreeNode* root;
    int order;
};


int main()
{
    cout << "B+ Trees test utility" << endl;
    return 0;
}