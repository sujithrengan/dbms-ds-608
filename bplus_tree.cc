#include <iostream>
#include <vector>
using namespace std;

class BPlusTreeNode
{
public:
    vector<int> keys;
    vector<BPlusTreeNode *> children;
    BPlusTreeNode *parent;
    BPlusTreeNode *next;
    BPlusTreeNode *prev;
    bool is_leaf;
    int order;

    BPlusTreeNode(int order, bool is_leaf)
    {
        this->order = order;
        this->is_leaf = is_leaf;
        this->parent = NULL;
        this->next = NULL;
        this->prev = NULL;
    }

    void print()
    {
        BPlusTreeNode *node = this;
        for(int i = 0; i < node->keys.size(); i++)
        {
            cout << node->keys[i] << " ";
        }
        cout << endl;
        if(node->is_leaf)
            return;
        for(int i = 0; i < node->children.size(); i++)
        {
            node->children[i]->print();
        }
    }

    BPlusTreeNode *insert(int key)
    {
        cout << "++" << __FUNCTION__ << " " << key << endl;
        BPlusTreeNode *new_node = nullptr;
        if (this->is_leaf)
        {
            new_node = _insert_into_leaf(key);
            cout << "--" << __FUNCTION__ << " " << key << endl;
            return new_node;
        }
        else
        {
            int i = 0;
            while (i < this->keys.size() && this->keys[i] < key)
            {
                i++;
            }
            new_node = this->children[i]->insert(key);
            if (new_node != nullptr)
            {
                int i = 0;
                while (i < this->keys.size() && this->keys[i] < new_node->keys[0])
                {
                    i++;
                }
                this->keys.insert(this->keys.begin() + i, new_node->keys[0]);
                this->children.insert(this->children.begin() + i + 1, new_node);
                new_node->parent = this;
                if (this->keys.size() > this->order)
                {
                    cout << "--" << __FUNCTION__ << " " << key << endl;
                    return _split_internal();
                }
            }
        }

        
        return nullptr;
    }

private:
    BPlusTreeNode *_split_internal()
    {
        cout << "++" << __FUNCTION__ << " " << endl;
        BPlusTreeNode *new_node = new BPlusTreeNode(this->order, false);
        int mid = this->keys.size() / 2;
        new_node->keys = vector<int>(this->keys.begin() + mid, this->keys.end());
        new_node->children = vector<BPlusTreeNode *>(this->children.begin() + mid + 1, this->children.end());
        this->keys = vector<int>(this->keys.begin(), this->keys.begin() + mid);
        this->children = vector<BPlusTreeNode *>(this->children.begin(), this->children.begin() + mid + 1);
        for (int i = 0; i < new_node->children.size(); i++)
        {
            new_node->children[i]->parent = new_node;
        }
        cout << "--" << __FUNCTION__ << " " << endl;
        return new_node;
    }

    BPlusTreeNode *_split_leaf()
    {
        cout << "++" << __FUNCTION__ << " " << endl;
        BPlusTreeNode *new_node = new BPlusTreeNode(this->order, true);
        int mid = this->keys.size() / 2;
        new_node->keys = vector<int>(this->keys.begin() + mid, this->keys.end());
        this->keys = vector<int>(this->keys.begin(), this->keys.begin() + mid);
        new_node->next = this->next;
        new_node->prev = this;
        this->next = new_node;
        cout << "--" << __FUNCTION__ << " " << endl;
        return new_node;
    }

    BPlusTreeNode *_insert_into_leaf(int key)
    {
        cout << "++" << __FUNCTION__ << " " << key << endl;
        int i = 0;
        BPlusTreeNode *new_node = nullptr;
        while (i < this->keys.size() && this->keys[i] < key)
        {
            i++;
        }
        this->keys.insert(this->keys.begin() + i, key);
        if (this->keys.size() > this->order)
        {
            new_node = _split_leaf();
        }
        if (new_node != nullptr)
            new_node->print();
        cout << "--" << __FUNCTION__ << " " << key << endl;
        return new_node;
    }
};

class BPlusTree
{
public:
    BPlusTree(int order)
    {
        this->order = order;
        this->root = new BPlusTreeNode(order, true);
    }

    void insert(int key)
    {
        BPlusTreeNode *new_node = this->root->insert(key);
        
        if (new_node != nullptr)
        {
            new_node->print();
            BPlusTreeNode *new_root = new BPlusTreeNode(this->order, false);
            new_root->keys.push_back(new_node->keys[0]);
            new_root->children.push_back(this->root);
            new_root->children.push_back(new_node);
            this->root->parent = new_root;
            new_node->parent = new_root;
            this->root = new_root;
        }
    }

    void print()
    {
        cout<<"----Tree----\n";
        root->print();
        cout<<"------------\n";
    }

private:
    BPlusTreeNode *root;
    int order;
};

void test_utility()
{
    BPlusTree *tree = new BPlusTree(5);
    for (int i = 1; i < 22; i++)
    {
        tree->insert(i);
    }
    
    tree->print();
}

int main()
{
    cout << "B+ Trees test utility\n"
         << "---------------------\n"
         << endl;
    test_utility();
    return 0;
}