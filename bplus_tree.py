import math
import random
from tabulate import tabulate

DEBUG_ENABLED = False
def debug_print(*args):
    if DEBUG_ENABLED:
        print(*args)
class BPlusTreeNode:
    def __init__(self, threshold, _is_leaf=False):
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
            ret += "\n" + str(child)
        return ret
    
    def pretty_keys(self):
        # return tabulate([self.keys], tablefmt="rounded_grid")
        return self.keys

    def insert(self, key):
        return self._insert_into_leaf(key) if self.is_leaf else self._insert_into_internal(key)

    def _sorted_index(self, key):
        i = 0
        while i < len(self.keys) and self.keys[i] <= key:
            i += 1
        return i

    def _insert_into_internal(self, key):
        ret_key, new_node = self.children[self._sorted_index(key)].insert(key)
        if new_node:
            debug_print(f"Internal node BEFORE: ")
            debug_print(self.pretty_keys())
            loc = self._sorted_index(ret_key)
            self.keys.insert(loc, ret_key)
            self.children.insert(loc + 1, new_node)
            new_node.parent = self
            debug_print(f"Internal node AFTER: ")
            debug_print(self.pretty_keys())
            if len(self.keys) > self.threshold:
                return self._split_internal()
        return (None, None)

    def _split_leaf(self):
        mid = len(self.keys) // 2
        new_node = BPlusTreeNode(self.threshold, True)
        new_node.keys = self.keys[mid:]
        new_node.prev = self
        new_node.next = self.next
        if self.next:
            self.next.prev = new_node
        self.next = new_node
        self.keys = self.keys[:mid]
        debug_print(f"Leaf node SPLIT AFTER: ")
        debug_print(self.pretty_keys())
        debug_print(new_node.pretty_keys())
        return (new_node.keys[0], new_node)

    def _insert_into_leaf(self, key):
        debug_print(f"Leaf node: BEFORE:")
        debug_print(self.pretty_keys())
        if key in self.keys:
            return (None, None)
        self.keys.append(key)
        self.keys.sort()
        debug_print(f"Leaf node: AFTER:")
        debug_print(self.pretty_keys())
        if len(self.keys) <= self.threshold:
            return (None, None)
        else:
            return self._split_leaf()

    def _split_internal(self):
        new_node = BPlusTreeNode(self.threshold, False)
        mid = len(self.keys) // 2
        new_node.keys = self.keys[mid + 1:]
        k_ret = self.keys[mid]
        new_node.children = self.children[mid + 1:]
        self.keys = self.keys[:mid]
        self.children = self.children[:mid + 1]
        for child in new_node.children:
            child.parent = new_node

        debug_print(f"Internal node SPLIT AFTER: ")
        debug_print(self.pretty_keys())
        debug_print(new_node.pretty_keys())
        return (k_ret, new_node)

    def is_sibling(self, node):
        return self.parent == node.parent

    def delete(self, key):
        if self.is_leaf:
            return self._delete_from_leaf(key)
        else:
            return self._delete_from_internal(key)

    def _delete_from_leaf(self, key):
        debug_print(f"Leaf node: BEFORE:")
        debug_print(self.pretty_keys())
        if key not in self.keys:
            return (None, None)
        
        self.keys.remove(key)
        debug_print(f"Leaf node: AFTER:")
        debug_print(self.pretty_keys())
        if len(self.keys) >= math.ceil((self.threshold+1)/2) or self.is_root:
            return (None, None)
        elif self.next and self.is_sibling(self.next) and len(self.next.keys) > math.ceil((self.threshold+1)/2):
            debug_print(f"Leaf node: BORROW BEFORE: SIBLING:")
            debug_print(self.next.pretty_keys())
            self.keys.append(self.next.keys.pop(0))
            debug_print(f"Leaf node: BORROW AFTER: LEAF:")
            debug_print(self.pretty_keys())
            debug_print(f"Leaf node: BORROW AFTER: SIBLING:")
            debug_print(self.next.pretty_keys())
            return (0, self.next.keys[0])
        elif self.prev and self.is_sibling(self.prev) and len(self.prev.keys) > math.ceil((self.threshold+1)/2):
            debug_print(f"Leaf node: BORROW BEFORE: SIBLING:")
            debug_print(self.prev.pretty_keys())
            self.keys.insert(0, self.prev.keys.pop())
            debug_print(f"Leaf node: BORROW AFTER: LEAF:")
            debug_print(self.pretty_keys())
            debug_print(f"Leaf node: BORROW AFTER: SIBLING:")
            debug_print(self.prev.pretty_keys())
            return (1, self.keys[0])
        elif self.next and self.is_sibling(self.next):
            debug_print(f"Leaf node: MERGE BEFORE: SIBLING:")
            debug_print(self.next.pretty_keys())
            self.keys.extend(self.next.keys)
            self.next = self.next.next
            if self.next:
                self.next.prev = self
            debug_print(f"Leaf node: MERGE AFTER LEAF:")
            debug_print(self.pretty_keys())
            return (-1, self.keys[0])
        elif self.prev and self.is_sibling(self.prev):
            debug_print(f"Leaf node: MERGE BEFORE: SIBLING:")
            debug_print(self.prev.pretty_keys())
            self.prev.keys.extend(self.keys)
            self.prev.next = self.next
            if self.next:
                self.next.prev = self.prev
            debug_print(f"Leaf node: MERGE AFTER LEAF:")
            debug_print(self.prev.pretty_keys())
            return (-2, self.prev.keys[0])
        else:
            return (None, None)

    def _delete_from_internal(self, key):
        loc = self._sorted_index(key)
        dir, min_key = self.children[loc].delete(key)
        if not min_key:
            return None, None
        debug_print(f"Internal node: BEFORE:")
        debug_print(self.pretty_keys())
        if dir >= 0:
            self.keys[loc - dir] = min_key
            debug_print(f"Internal node: AFTER: ")
            debug_print(self.pretty_keys())
            return None, None
        elif dir <0:
            if dir == -1:
                self.keys.pop(loc)
                self.children = self.children.pop(loc)
            else:
                self.keys.pop(loc - 1)
                self.children = self.children.pop(loc - 1)

        debug_print(f"Internal node: AFTER: ")
        debug_print(self.pretty_keys())
        if len(self.keys) >= math.ceil((self.threshold+1)/2):
            return None, None
        else:
            return dir, self.keys[0]


    def search(self, key):
        if self.is_leaf:
            ret = [key] if key in self.keys else []
            if(ret):
                debug_print(f"FOUND KEY: {ret}")
            else:
                debug_print(f"KEY NOT FOUND")
            return ret
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
                        if ret:
                            debug_print(f"Leaf nodes iterated: FOUND {len(ret)} KEYS: {ret}")
                        else:
                            debug_print(f"Leaf nodes iterated: FOUND NO KEYS")
                        return ret
                node = node.next
            if ret:
                debug_print(f"Leaf nodes iterated: FOUND {len(ret)} KEYS: {ret}")
            else:
                debug_print(f"Leaf nodes iterated: FOUND NO KEYS")
            return ret
        else:
            for i in range(len(self.keys)):
                if start < self.keys[i]:
                    return self.children[i].range_search(start, end)
            return self.children[-1].range_search(start, end)


class BPlusTree:
    def __init__(self, order, is_sparse=False):
        self.order = order
        self.is_sparse = is_sparse
        self.threshold = math.ceil(order / 2) if self.is_sparse else order
        self.root = BPlusTreeNode(self.threshold, True)

    def insert(self, key):
        debug_print(f"[B+ {self.order} {'sparse' if self.is_sparse else 'dense'}] ++Inserting {key}")
        ret_key, new_node = self.root.insert(key)
        if new_node:
            new_root = BPlusTreeNode(self.threshold, False)
            new_root.is_root = True
            new_root.keys.append(ret_key)
            new_root.children.append(self.root)
            new_root.children.append(new_node)
            self.root.parent = new_node.parent = self.root = new_root
            debug_print(f"Root node: NEW: ", new_root.keys)
        debug_print(f"[B+ {self.order} {'sparse' if self.is_sparse else 'dense'}] --Inserting {key}\n")
    
    def build(self, keys):
        for key in keys:
            self.insert(key)

    def delete(self, key):
        debug_print(f"[B+ {self.order} {'sparse' if self.is_sparse else 'dense'}] ++Deleting {key}")
        _, new_node = self.root.delete(key)
        if new_node:
            self.root = new_node
            self.root.parent = None
            debug_print(f"Root node: NEW: ", self.root.keys)
        debug_print(f"[B+ {self.order} {'sparse' if self.is_sparse else 'dense'}] --Deleting {key}\n")

    def search(self, key):
        debug_print(f"[B+ {self.order} {'sparse' if self.is_sparse else 'dense'}] ++Searching {key}")
        ret =  self.root.search(key)
        debug_print(f"[B+ {self.order} {'sparse' if self.is_sparse else 'dense'}] --Searching {key}\n")
        return ret

    def range_search(self, start, end):
        debug_print(f"[B+ {self.order} {'sparse' if self.is_sparse else 'dense'}] ++RangeSearching ({start}, {end})")
        ret = self.root.range_search(start, end)
        debug_print(f"[B+ {self.order} {'sparse' if self.is_sparse else 'dense'}] --RangeSearching ({start}, {end})\n")
        return ret

    def __repr__(self) -> str:
        ret = "---- B+ Tree ----\n"
        ret += str(self.root)
        ret += "\n-----------------"
        return ret


def generate_keys(count = 10000, low = 100000, high=200000):
    return random.sample(range(low, high), count)

def generate_key(low = 100000, high=200000):
    return random.randint(low, high)

def debug():
    tree = BPlusTree(13)
    for i in range(1, 21):
        tree.insert(i)
    print(tree)
    tree.delete(18)
    tree.delete(1)
    print(tree)
    for i in range(9, 15):
        tree.delete(i)
        print(tree)
    print(tree.search(1))
    print(tree.range_search(13, 22))


def build_trees():
    dense_tree_13 = BPlusTree(13, is_sparse=False)
    dense_tree_13.build(keys)

    sparse_tree_13 = BPlusTree(13, is_sparse=True)
    sparse_tree_13.build(keys)

    dense_tree_24 = BPlusTree(24, is_sparse=False)
    dense_tree_24.build(keys)

    sparse_tree_24 = BPlusTree(24, is_sparse=True)
    sparse_tree_24.build(keys)

    return dense_tree_13, dense_tree_24, sparse_tree_13, sparse_tree_24

def random_insert_delete(tree, keys, count=5):
    for _ in range(count):
        key = generate_key()
        tree.insert(key)
    for _ in range(count):
        key = random.sample(keys, 1)[0]
        tree.delete(key)

def validate_search(ret, key, keys):
    if (ret and ret[0]!=key) or (key in keys and not key in ret):
        print("Search validation failed")

def validate_range_search(ret, start, end, keys):
    if not ret:
        if any([key >= start and key <= end for key in keys]):
            print("Range search validation failed")
    else:
        rkeys = sorted([key for key in keys if key >= start and key <= end])
        ret = sorted(ret)
        if len(ret) != len(rkeys):
            print("Range search validation failed")
        else:
            for i in range(len(ret)):
                if ret[i] != rkeys[i]:
                    print("Range search validation failed")

def random_search(tree, key, count=5):
    for _ in range(count):
        start = random.randint(100000, 200000)
        end = start + random.randint(1, 100)
        ret = tree.range_search(start, end)
        validate_range_search(ret, start, end, keys)

    for _ in range(count):
        key = random.randint(100000, 200000)
        ret = tree.search(key)
        validate_search(ret, key, keys)

def run_experiments(dense_tree_13, dense_tree_24, sparse_tree_13, sparse_tree_24, keys):
    global DEBUG_ENABLED
    DEBUG_ENABLED = True

    dense_tree_13.insert(generate_key())
    dense_tree_13.insert(generate_key())
    dense_tree_24.insert(generate_key())
    dense_tree_24.insert(generate_key())

    sparse_tree_13.delete(random.sample(keys,1)[0])
    sparse_tree_13.delete(random.sample(keys,1)[0])
    sparse_tree_24.delete(random.sample(keys,1)[0])
    sparse_tree_24.delete(random.sample(keys,1)[0])

    random_insert_delete(dense_tree_13, keys)
    random_insert_delete(dense_tree_24, keys)
    random_insert_delete(sparse_tree_13, keys)
    random_insert_delete(sparse_tree_24, keys)

    random_search(dense_tree_13, keys)
    random_search(dense_tree_24, keys)
    random_search(sparse_tree_13, keys)
    random_search(sparse_tree_24, keys)

random.seed(1)
keys = generate_keys()

dense_tree_13, dense_tree_24, sparse_tree_13, sparse_tree_24 = build_trees()
run_experiments(dense_tree_13, dense_tree_24, sparse_tree_13, sparse_tree_24, keys)

'''
Doubts:
1. Number of insert/delete operations in c3
2. Number of search operations in c4
3. Should i print all leaf nodes in range search iteration?
'''

