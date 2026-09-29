KEY_CHARS = 4
BASE = 27

def name_to_key(name: str) -> int:
    chars = name.lower()[:KEY_CHARS]
    key = 0
    for ch in chars:
        if 'a' <= ch <= 'z':
            code = ord(ch) - ord('a') + 1
        else:
            code = 0
        key = key * BASE + code

    padding = KEY_CHARS - len(chars)
    key *= BASE ** padding

    return key

def name_to_key_full(name: str) -> int:
    prefix = name_to_key(name)

    suffix_chars = name.lower()[KEY_CHARS:]
    rolling = 0
    for ch in suffix_chars:
        rolling = rolling * 31 + ord(ch)

    SUFFIX_MOD = BASE ** KEY_CHARS
    return prefix * SUFFIX_MOD + (rolling % SUFFIX_MOD)

class BPlusNode:
    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []
        self.parent = None
        self.next = None

    def __repr__(self):
        return f"{'Leaf' if self.is_leaf else 'Node'}{self.keys}"

class BPlusTree:
    def __init__(self, order=4, max_depth=3, use_full_hash=True):
        self.root          = BPlusNode(is_leaf=True)
        self.order         = order
        self.min_keys      = (order + 1) // 2 
        self.max_depth     = max_depth
        self._depth        = 1
        self._hash_fn      = name_to_key_full if use_full_hash else name_to_key

        max_capacity = (order - 1) * (order ** (max_depth - 1))
        print(f"\n[BPlusTree] order={order}, max_depth={max_depth}, "
              f"min_keys={self.min_keys}, max_capacity≈{max_capacity} records")

        self._cached_leaf  = None
        self._cache_hits   = 0
        self._cache_misses = 0


    def _check_depth_before_split(self):
        if self._depth + 1 > self.max_depth:
            raise OverflowError(
                f"\n  Дерево не може рости далі: поточна глибина {self._depth}, "
                f"ліміт {self.max_depth}.\n"
                f"  Рішення: збільшіть order (зараз {self.order}) або max_depth.\n"
                f"  При order={self.order} і max_depth={self.max_depth} "
                f"максимум ≈ {(self.order-1) * self.order**(self.max_depth-1)} записів."
            )


    def _find_leaf(self, key):
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        return node


    def insert(self, name: str, phone: str):
        self._invalidate_cache()
        key  = self._hash_fn(name)
        leaf = self._find_leaf(key)

        idx = 0
        while idx < len(leaf.keys) and leaf.keys[idx] < key:
            idx += 1

        leaf.keys.insert(idx, key)
        leaf.children.insert(idx, (name, phone))

        if len(leaf.keys) >= self.order:
            self._split_leaf(leaf)

    def _split_leaf(self, leaf):
        new_leaf = BPlusNode(is_leaf=True)
        mid = len(leaf.keys) // 2

        new_leaf.keys     = leaf.keys[mid:]
        new_leaf.children = leaf.children[mid:]
        leaf.keys         = leaf.keys[:mid]
        leaf.children     = leaf.children[:mid]

        new_leaf.next = leaf.next
        leaf.next     = new_leaf

        if leaf is self.root:
            self._check_depth_before_split()
            new_root = BPlusNode(is_leaf=False)
            new_root.keys     = [new_leaf.keys[0]]
            new_root.children = [leaf, new_leaf]
            leaf.parent       = new_root
            new_leaf.parent   = new_root
            self.root         = new_root
            self._depth      += 1
        else:
            self._insert_into_parent(leaf, new_leaf.keys[0], new_leaf)

    def _insert_into_parent(self, left, key, right):
        parent = left.parent
        idx    = parent.children.index(left)
        parent.keys.insert(idx, key)
        parent.children.insert(idx + 1, right)
        right.parent = parent

        if len(parent.keys) >= self.order:
            self._split_internal(parent)

    def _split_internal(self, node):
        new_node     = BPlusNode(is_leaf=False)
        mid          = len(node.keys) // 2
        up_key       = node.keys[mid]

        new_node.keys     = node.keys[mid + 1:]
        new_node.children = node.children[mid + 1:]
        for child in new_node.children:
            child.parent = new_node

        node.keys     = node.keys[:mid]
        node.children = node.children[:mid + 1]

        if node is self.root:
            self._check_depth_before_split()
            new_root = BPlusNode(is_leaf=False)
            new_root.keys     = [up_key]
            new_root.children = [node, new_node]
            node.parent       = new_root
            new_node.parent   = new_root
            self.root         = new_root
            self._depth      += 1
        else:
            self._insert_into_parent(node, up_key, new_node)


    def _is_key_in_cached_leaf(self, key) -> bool:
        leaf = self._cached_leaf
        if leaf is None or not leaf.keys:
            return False
        return leaf.keys[0] <= key <= leaf.keys[-1]

    def _invalidate_cache(self):
        self._cached_leaf = None


    def search(self, name: str):
        key = self._hash_fn(name)

        if self._is_key_in_cached_leaf(key):
            self._cache_hits += 1
            leaf = self._cached_leaf
            for i, k in enumerate(leaf.keys):
                if k == key:
                    return leaf.children[i]
            return None
        
        self._cache_misses += 1
        leaf = self._find_leaf(key)
        self._cached_leaf = leaf

        for i, k in enumerate(leaf.keys):
            if k == key:
                return leaf.children[i]
        return None

    def search_greater(self, name: str):
        key = self._hash_fn(name)

        if self._is_key_in_cached_leaf(key):
            self._cache_hits += 1
            leaf = self._cached_leaf
        else:
            self._cache_misses += 1
            leaf = self._find_leaf(key)
            self._cached_leaf = leaf

        result = []
        while leaf:
            for i, k in enumerate(leaf.keys):
                if k > key:
                    result.append(leaf.children[i])
            leaf = leaf.next
        return result

    def search_less(self, name: str):
        key  = self._hash_fn(name)
        node = self.root
        while not node.is_leaf:
            node = node.children[0]
        result = []
        while node:
            for i, k in enumerate(node.keys):
                if k < key:
                    result.append(node.children[i])
            node = node.next
        return result


    def delete(self, name: str) -> bool:
        self._invalidate_cache()
        key  = self._hash_fn(name)
        leaf = self._find_leaf(key)

        if key not in leaf.keys:
            return False

        idx = leaf.keys.index(key)
        leaf.keys.pop(idx)
        leaf.children.pop(idx)

        if leaf is self.root:
            return True

        if len(leaf.keys) >= self.min_keys:
            if idx == 0 and leaf.keys:
                self._update_parent_key(leaf)
            return True

        if self._borrow_from_sibling(leaf):
            return True

        self._merge_leaf(leaf)
        return True

    def _update_parent_key(self, leaf):
        if not leaf.parent or not leaf.keys:
            return
        parent = leaf.parent
        try:
            child_idx = parent.children.index(leaf)
        except ValueError:
            return
        if child_idx > 0:
            parent.keys[child_idx - 1] = leaf.keys[0]

    def _get_siblings(self, node):
        parent = node.parent
        idx    = parent.children.index(node)
        left   = parent.children[idx - 1] if idx > 0 else None
        right  = parent.children[idx + 1] if idx < len(parent.children) - 1 else None
        return left, right, idx

    def _borrow_from_sibling(self, leaf) -> bool:
        parent         = leaf.parent
        left, right, idx = self._get_siblings(leaf)

        if right and len(right.keys) > self.min_keys:
            leaf.keys.append(right.keys.pop(0))
            leaf.children.append(right.children.pop(0))
            if right.keys:
                parent.keys[idx] = right.keys[0]
            return True

        if left and len(left.keys) > self.min_keys:
            leaf.keys.insert(0, left.keys.pop(-1))
            leaf.children.insert(0, left.children.pop(-1))
            parent.keys[idx - 1] = leaf.keys[0]
            return True

        return False

    def _merge_leaf(self, leaf):
        parent           = leaf.parent
        left, right, idx = self._get_siblings(leaf)

        if right:
            leaf.keys.extend(right.keys)
            leaf.children.extend(right.children)
            leaf.next = right.next
            parent.keys.pop(idx)
            parent.children.pop(idx + 1)
        else:
            left.keys.extend(leaf.keys)
            left.children.extend(leaf.children)
            left.next = leaf.next
            parent.keys.pop(idx - 1)
            parent.children.pop(idx)

        if parent is self.root:
            if not parent.keys:
                self.root        = parent.children[0]
                self.root.parent = None
                self._depth     -= 1
        elif len(parent.keys) < self.min_keys:
            self._fix_internal(parent)

    def _fix_internal(self, node):
        parent           = node.parent
        left, right, idx = self._get_siblings(node)

        if right and len(right.keys) > self.min_keys:
            node.keys.append(parent.keys[idx])
            parent.keys[idx] = right.keys.pop(0)
            child = right.children.pop(0)
            child.parent = node
            node.children.append(child)
            return

        if left and len(left.keys) > self.min_keys:
            node.keys.insert(0, parent.keys[idx - 1])
            parent.keys[idx - 1] = left.keys.pop(-1)
            child = left.children.pop(-1)
            child.parent = node
            node.children.insert(0, child)
            return

        if right:
            node.keys.append(parent.keys.pop(idx))
            node.keys.extend(right.keys)
            for child in right.children:
                child.parent = node
            node.children.extend(right.children)
            parent.children.pop(idx + 1)
        else:
            left.keys.append(parent.keys.pop(idx - 1))
            left.keys.extend(node.keys)
            for child in node.children:
                child.parent = left
            left.children.extend(node.children)
            parent.children.pop(idx)
            node = left

        if parent is self.root:
            if not parent.keys:
                self.root        = parent.children[0]
                self.root.parent = None
                self._depth     -= 1
        elif len(parent.keys) < self.min_keys:
            self._fix_internal(parent)


    def print_tree(self):
        print(f"\nB+ Tree  order={self.order}, "
              f"depth={self._depth}/{self.max_depth}")
        if not self.root.keys and not self.root.children:
            print("Empty tree")
            return

        queue = [(self.root, 0)]
        cur_level, line = 0, []
        while queue:
            node, level = queue.pop(0)
            if level != cur_level:
                print(f"Level {cur_level}: " + "   ".join(line))
                line, cur_level = [], level
            if node.is_leaf:
                names = [c[0] for c in node.children]
                line.append(f"[{', '.join(names)}]")
            else:
                line.append(f"({', '.join(str(k) for k in node.keys)})")
                for child in node.children:
                    queue.append((child, level + 1))
        if line:
            print(f"Level {cur_level}: " + "   ".join(line))

        node  = self.root
        while not node.is_leaf:
            node = node.children[0]
        chain = []
        while node:
            chain.append([c[0] for c in node.children])
            node = node.next
        print("Linked chain: " + " => ".join(str(b) for b in chain))
        print()


if __name__ == "__main__":
    print("\nHash functions:")
    names_test = ["Anna", "Annabelle", "Boris", "Charlie", "David", "Egor",
                  "Fiona", "George", "Helen", "Igor", "John", "Kate", "Leo", "Mia"]
    print(f"{'name':<12} {'rolling hash':>16}  {'order-preserving':>18}  {'combined':>20}")
    print("-" * 72)

    def rolling(name):
        k = 0
        for ch in name.lower(): k = k * 31 + ord(ch)
        return k

    for n in names_test:
        print(f"{n:<12} {rolling(n):>16}  {name_to_key(n):>18}  {name_to_key_full(n):>20}")

    tree = BPlusTree(order=4, max_depth=3, use_full_hash=True)

    records = [
        ("Boris",   "380-95-123-45-68"),
        ("Charlie", "380-95-123-45-69"),
        ("David",   "380-95-123-45-70"),
        ("Egor",    "380-95-123-45-71"),
        ("Annabelle", "380-95-123-45-72"),
        ("Anna",    "380-95-123-45-72"),
        ("Fiona",   "380-95-123-45-73"),
        ("George",  "380-95-123-45-74"),
        ("Helen",   "380-95-123-45-75"),
        ("Igor",    "380-95-123-45-76"),
        ("John",    "380-95-123-45-77"),
        ("Kate",    "380-95-123-45-78"),
        ("Leo",     "380-95-123-45-79"),
        ("Mia",     "380-95-123-45-80"),
    ]
    for name, phone in records:
        tree.insert(name, phone)

    print("\nTree after insertions:")
    tree.print_tree()

    print("\nSearches:")
    for name in ["Anna", "David", "Zara"]:
        result = tree.search(name)
        print(f"Search('{name}') => {result}")

    print("\nSearch after Fiona")
    for r in tree.search_greater("Fiona"):
        print(f"{r[0]}")

    print("\nSearch before David")
    for r in tree.search_less("David"):
        print(f"{r[0]}")

    print("\nDeletions:")
    for name in ["Anna", "Egor", "Charlie", "Peter", "Helen", "Fiona"]:
        ok = tree.delete(name)
        print(f"Delete('{name}') => {'OK' if ok else 'Not found'}")
    tree.print_tree()

    def search_verbose(tree, name):
        hits_before = tree._cache_hits
        result = tree.search(name)
        hit = tree._cache_hits > hits_before
        status = "Cache used" if hit else "Cache not used"
        name_str = result[0] if result else "None"
        print(f"Search('{name}') => {name_str:<12}  [{status}]")

    search_verbose(tree, "Annabelle")
    search_verbose(tree, "Boris")
    search_verbose(tree, "Charlie")
    search_verbose(tree, "David")
    search_verbose(tree, "George")
    search_verbose(tree, "Helen")
