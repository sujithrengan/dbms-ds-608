import math

class BPlusTreeNode:
    def __init__(self, threshold, _is_leaf = False):
        self.threshold = threshold
        self.keys = []
        self.children = []
        self.is_leaf = _is_leaf
        self.next = None
        self.prev = None
        self.parent = None
        self.is_root = False
    
    def __repr__(self):
        ret = " ".join([str(key) for key in self.keys])
        for child in self.children:
            ret += "\n"+str(child)
        return ret
    
    def insert(self, key):
        return self._insert_into_leaf(key) if self.is_leaf else self._insert_into_internal(key)
    
    def _sorted_index(self, key):
        i = 0
        while i<len(self.keys) and self.keys[i]<key:
            i+=1
        return i
    
    def _insert_into_internal(self, key):
        ret_key, new_node = self.children[self._sorted_index(key)].insert(key)
        if new_node:
            loc = self._sorted_index(ret_key)
            self.keys.insert(loc, ret_key)
            self.children.insert(loc+1, new_node)
            new_node.parent = self
            if len(self.keys)>self.threshold:
                return self._split_internal()
        return (None, None)
    
    def _split_leaf(self):
        mid = len(self.keys)//2
        new_node = BPlusTreeNode(self.threshold, True)
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
        if len(self.keys) <= self.threshold:
            return (None, None)
        else:
            return self._split_leaf()
    
    def _split_internal(self):
        new_node = BPlusTreeNode(self.threshold, False)
        mid = len(self.keys)//2
        new_node.keys = self.keys[mid+1:]
        k_ret = self.keys[mid]
        new_node.children = self.children[mid+1:]
        self.keys = self.keys[:mid]
        self.children = self.children[:mid+1]
        for child in new_node.children:
            child.parent = new_node
        return (k_ret, new_node)

    def is_sibling(self, node):
        return self.parent == node.parent

    def delete(self, key):
        if self.is_leaf:
            return self._delete_from_leaf(key)
        else:
            return self._delete_from_internal(key)
    
    def _delete_from_leaf(self, key):
        if key in self.keys:
            self.keys.remove(key)
            if len(self.keys)<math.floor((self.threshold+1)/2) or self.is_root:
                return (None, None)
            elif self.next and self.is_sibling(self.next) and len(self.next.keys)>math.floor((self.threshold+1)/2):
                self.keys.append(self.next.keys.pop(0))
                return (0, self.next.keys[0])
            elif self.prev and self.is_sibling(self.prev) and len(self.prev.keys)>math.floor((self.threshold+1)/2):
                self.keys.insert(0, self.prev.keys.pop())
                return (1, self.keys[0])
            elif self.next and self.is_sibling(self.next):
                self.keys.extend(self.next.keys)
                self.next = self.next.next
                if self.next:
                    self.next.prev = self
                return (-1, self.keys[0])
            elif self.prev and self.is_sibling(self.prev):
                self.prev.keys.extend(self.keys)
                self.prev.next = self.next
                if self.next:
                    self.next.prev = self.prev
                return (-1, self.prev.keys[0])
            else:
                return (0, self.keys[0])
        return (None, None)
    
    def _delete_from_internal(self, key):
        loc = self._sorted_index(key)
        dir, min_key = self.children[loc].delete(key)
        if not min_key:
            return (None, None)
        if dir > 0:
            self.keys[loc - dir] = min_key
            if loc == 0 or loc == 1:
                return (1, self.keys[0])
        


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
    def __init__(self, order, is_sparse=False):
        self.is_sparse = is_sparse
        self.order = order
        threshold = math.ceil(order/2) if is_sparse else order
        self.root = BPlusTreeNode(threshold, True)

    def insert(self, key):
        ret_key, new_node = self.root.insert(key)
        if new_node:
            new_root = BPlusTreeNode(self.order, False)
            new_root.is_root = True
            new_root.keys.append(ret_key)
            new_root.children.append(self.root)
            new_root.children.append(new_node)
            self.root.parent = new_node.parent = self.root = new_root

    def delete(self, key):
        _, new_node = self.root.delete(key)
        if new_node:
            self.root = new_node

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
for i in range(1, 25):
    tree.insert(i)
print(tree)
tree.delete(23)
tree.delete(24)
print(tree)
print(tree.search(1))
print(tree.range_search(13, 22))