class BPlusTreeNode:
    def __init__(self, _order, _is_leaf = False):
        self.order = _order
        self.keys = []
        self.children = []
        self.is_leaf = _is_leaf
        self.next = None
        self.prev = None
        self.parent = None
    
    def __repr__(self):
        ret = " ".join([str(key) for key in self.keys])
        for child in self.children:
            ret += "\n"+str(child)
        return ret
    
    def insert(self, key):
        return self._insert_into_leaf(key) if self.is_leaf else self._insert_into_internal(key)
    
    def _insert_into_internal(self, key):
        i = 0
        while i<len(self.keys) and self.keys[i]<key:
            i+=1
        ret_key, new_node = self.children[i].insert(key)
        if new_node:
            i = 0
            while i<len(self.keys) and self.keys[i]<ret_key:
                i+=1
            self.keys.insert(i, ret_key)
            self.children.insert(i+1, new_node)
            new_node.parent = self
            if len(self.keys)>self.order:
                return self._split_internal()
        return (None, None)
    
    def _split_leaf(self):
        mid = len(self.keys)//2
        new_node = BPlusTreeNode(self.order, True)
        new_node.keys = self.keys[mid:]
        new_node.prev = self
        new_node.next = self.next
        if self.next:
            self.next.prev = new_node
        self.next = new_node
        self.keys = self.keys[:mid]
        return (new_node.keys[0], new_node)

    def _insert_into_leaf(self, key):
        self.keys.append(key)
        self.keys.sort()
        if len(self.keys) <= self.order:
            return (None, None)
        else:
            return self._split_leaf()
    
    def _split_internal(self):
        new_node = BPlusTreeNode(self.order, False)
        mid = len(self.keys)//2
        new_node.keys = self.keys[mid+1:]
        k_ret = self.keys[mid]
        new_node.children = self.children[mid+1:]
        self.keys = self.keys[:mid]
        self.children = self.children[:mid+1]
        for child in new_node.children:
            child.parent = new_node
        return (k_ret, new_node)

    def search(self, key):
        if self.is_leaf:
            return True if key in self.keys else False
        else:
            for i in range(len(self.keys)):
                if key < self.keys[i]:
                    return self.children[i].search(key)
            return self.children[-1].search(key)
    
    def range_search(self, start, end):
        if self.is_leaf:
            node, ret = self, []
            while node:
                for key in node.keys:
                    if key >= start and key <= end:
                        ret.append(key)
                    elif key > end:
                        return ret
                node = node.next
            return ret
        else:
            for i in range(len(self.keys)):
                if start < self.keys[i]:
                    return self.children[i].range_search(start, end)
            return self.children[-1].range_search(start, end)

class BPlusTree:
    def __init__(self, order):
        self.order = order
        self.root = BPlusTreeNode(order, True)

    def insert(self, key):
        ret_key, new_node = self.root.insert(key)
        if new_node:
            new_root = BPlusTreeNode(self.order, False)
            new_root.keys.append(ret_key)
            new_root.children.append(self.root)
            new_root.children.append(new_node)
            self.root.parent = new_node.parent = self.root = new_root

    def search(self, key):
        return self.root.search(key)

    def range_search(self, start, end):
        return self.root.range_search(start, end)
    
    def __repr__(self) -> str:
        ret = "---- B+ Tree ----\n"
        ret += str(self.root)
        ret += "\n-----------------"
        return ret

tree = BPlusTree(5)
for i in range(1, 22):
    tree.insert(i)
print(tree)
print(tree.search(0))
print(tree.range_search(13, 100))