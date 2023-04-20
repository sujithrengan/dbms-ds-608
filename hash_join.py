import random, string, math

class Relation:
    def __init__(self, name, base_address, size=0, ref = [], refKeys = set()):
        self.name = name
        self.base_address = base_address
        self.size = size
        self.ref = ref
        self.refKeys = refKeys
        self.metrics = [0]

class VirtualDiskBlock:
    def __init__(self, block_size, data=[]):
        self.block_size = block_size
        self.data = [None]*block_size
        for i in range(min(block_size, len(data))):
            self.data[i] = data[i]

    def get(self):
        return self.data
    
    def __repr__(self):
        return str(self.data)
    

class VirtualDisk:
    def __init__(self):
        self.BLOCK_SIZE = 8
        self.BUCKET_CAP = 200
        self.array = [None] * self.BUCKET_CAP ** 2
        self.cursor = 0
        self.io_count = 0
        self.bucket_base = 0

    def readBlock(self, block_id):
        self.io_count += 1
        return self.array[block_id]

    def writeBlockSeq(self, block):
        self.array[self.cursor] = block
        self.cursor += 1
    
    def writeBlock(self, block, block_id):
        self.io_count += 1
        self.array[block_id] = block
    
    def getWriteCursor(self):
        return self.cursor
    
class VirtualMemory:
    def __init__(self):
        self.SIZE = 15
        self.array = [None] * self.SIZE * 8
        self.base_address = 0
        self.cache = [None] * 3

    def writeToDiskSeq(self, disk, mem_offset = 0):
        block = VirtualDiskBlock(disk.BLOCK_SIZE, self.array[mem_offset:mem_offset+disk.BLOCK_SIZE])
        disk.writeBlockSeq(block)
    
    def writeToDiskLoc(self, disk, block_id, mem_offset = 0):
        block = VirtualDiskBlock(disk.BLOCK_SIZE, self.array[mem_offset:mem_offset+disk.BLOCK_SIZE])
        disk.writeBlock(block, block_id)

    def readFromDisk(self, disk,  block_id, mem_offset = 0):
        block = disk.readBlock(block_id)
        for i in range(disk.BLOCK_SIZE):
            self.array[mem_offset + i] = block.data[i]
    
    def flush(self):
        for i in range(self.base_address, self.SIZE*8):
            self.array[i] = None

def generateRandomWord():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

def generateRandomKey(low, high):
    return random.randint(low, high)

def generateRelationBC(disk, size=5000):
    base_address = disk.getWriteCursor()
    ref, refKeys = [], set()
    for off in range(size//disk.BLOCK_SIZE):
        block = VirtualDiskBlock(disk.BLOCK_SIZE)
        for blk in range(disk.BLOCK_SIZE):
            while True:
                B = generateRandomKey(10000, 50000)
                if B not in refKeys:
                    refKeys.add(B)
                    break
            C = generateRandomWord()
            ref.append((B, C))
            block.data[blk] = (B, C)
        disk.writeBlockSeq(block)
    disk.bucket_base += size//disk.BLOCK_SIZE
    return Relation("BC", base_address, size, ref, refKeys)

def generateRelationABFromBKeys(disk, refBKeys, size = 1000):
    base_address = disk.getWriteCursor()
    ref, refKeys = [], set()
    for off in range(size//disk.BLOCK_SIZE):
        block = VirtualDiskBlock(disk.BLOCK_SIZE)
        for blk in range(disk.BLOCK_SIZE):
            A = generateRandomWord()
            B = random.choice(list(refBKeys))
            refKeys.add(B)
            ref.append((B, A))
            block.data[blk] = (B, A)
        disk.writeBlockSeq(block)
    disk.bucket_base += size//disk.BLOCK_SIZE        
    return Relation("AB", base_address, size, ref, refKeys)

def generateRelationAB(disk, size = 1200):
    base_address = disk.getWriteCursor()
    ref, refKeys = [], set()
    for off in range(size//disk.BLOCK_SIZE):
        block = VirtualDiskBlock(disk.BLOCK_SIZE)
        for blk in range(disk.BLOCK_SIZE):
            A = generateRandomWord()
            B = generateRandomKey(20000, 30000)
            refKeys.add(B)
            ref.append((B, A))
            block.data[blk] = (B, A)
        disk.writeBlockSeq(block)
    disk.bucket_base += size//disk.BLOCK_SIZE     
    return Relation("AB2", base_address, size, ref, refKeys)

def jenkinsHash(key, size):
    # return key % size
    hash = 0
    key = str(key)
    for c in key:
        hash += ord(c)
        hash += (hash << 10)
        hash ^= (hash >> 6)
    hash += (hash << 3)
    hash ^= (hash >> 11)
    hash += (hash << 15)
    return hash % size

def printRelation(disk, R):
    print("Relation", R.name, ":", R.size//disk.BLOCK_SIZE, "blocks")
    for i in range(R.size//disk.BLOCK_SIZE):
        print(disk.readBlock(R.base_address + i))

def getRIndex(R):
    return 0 if R.name == "BC" else 1 if R.name == "AB" else 2

def generateBuckets(mem, disk, R, num_buckets):
    r = getRIndex(R)
    disk.cursor = disk.bucket_base + r * num_buckets * disk.BUCKET_CAP
    mem.cache[r] = [0] * num_buckets
    for i in range(R.size//disk.BLOCK_SIZE):
        mem.readFromDisk(disk, R.base_address + i , mem.base_address)
        bucket_base = mem.base_address + disk.BLOCK_SIZE
        for j in range(mem.base_address, mem.base_address + disk.BLOCK_SIZE):
            key, val = mem.array[j]
            hash = jenkinsHash(key, num_buckets)
            mem.array[bucket_base + hash * disk.BLOCK_SIZE + mem.cache[r][hash]%disk.BLOCK_SIZE] = (key, val)
            mem.cache[r][hash] += 1
            if mem.cache[r][hash]%disk.BLOCK_SIZE == 0:
                mem.writeToDiskLoc(disk, disk.cursor + hash * disk.BUCKET_CAP + mem.cache[r][hash]//disk.BLOCK_SIZE - 1, bucket_base + hash * disk.BLOCK_SIZE)
                for i in range(disk.BLOCK_SIZE):
                    mem.array[bucket_base + hash * disk.BLOCK_SIZE + i] = None

    for bucket in range(num_buckets):
        if mem.cache[r][bucket]%disk.BLOCK_SIZE > 0:
            mem.writeToDiskLoc(disk, disk.cursor + bucket * disk.BUCKET_CAP + mem.cache[r][bucket]//disk.BLOCK_SIZE, bucket_base + bucket * disk.BLOCK_SIZE)
    mem.flush()


def hashJoin(mem, disk, R1, R2):
    num_buckets = mem.SIZE - 1 # 1 block for reading
    r1, r2 = getRIndex(R1), getRIndex(R2)
    begin_io_count = disk.io_count
    if(mem.cache[r1] == None):
        generateBuckets(mem, disk, R1, num_buckets)
        R1.metrics[0] = disk.io_count - begin_io_count
    if(mem.cache[r2] == None):
        r2_begin_io_count = disk.io_count
        generateBuckets(mem, disk, R2, num_buckets)
        R2.metrics[0] = disk.io_count - r2_begin_io_count

    disk.cursor = disk.bucket_base
    
    joinResults = []
    for bucket in range(num_buckets):
        for i in range(math.ceil(mem.cache[r2][bucket]/disk.BLOCK_SIZE)):
            mem.readFromDisk(disk, disk.cursor + r2 * num_buckets * disk.BUCKET_CAP + bucket * disk.BUCKET_CAP + i, mem.base_address + (i+1)*disk.BLOCK_SIZE)
        
        for j in range(math.ceil(mem.cache[r1][bucket]/disk.BLOCK_SIZE)):
            mem.readFromDisk(disk, disk.cursor + bucket * disk.BUCKET_CAP + j, mem.base_address)
            for tuple in mem.array[mem.base_address + disk.BLOCK_SIZE:mem.base_address + disk.BLOCK_SIZE + mem.cache[r2][bucket]]:
                keyR2, valR2 = tuple
                for l in range(disk.BLOCK_SIZE):
                    if mem.array[mem.base_address + l] == None:
                        break
                    keyR1, valR1 = mem.array[mem.base_address + l]
                    if keyR2 == keyR1:
                        # print(key1, val1, val2)
                        joinResults.append((keyR2, valR1, valR2))


    return joinResults, disk.io_count - begin_io_count

def verifyHashJoin(joinResults, R1, R2):
    for key, valR1, valR2 in joinResults:
        if (key, valR1) not in R1.ref or (key, valR2) not in R2.ref:
            print("Error:", key, valR1, valR2)
            return False
    print(f"Join verified for {R1.name} and {R2.name}. Total tuples: {len(joinResults)}")
    return True


random.seed(23)
disk = VirtualDisk()
mem = VirtualMemory()


relationBC = generateRelationBC(disk)
relationAB = generateRelationABFromBKeys(disk, relationBC.refKeys)
relationAB2 = generateRelationAB(disk)

joinResults, io_count = hashJoin(mem, disk, relationBC, relationAB)
verifyHashJoin(joinResults, relationBC, relationAB)
print(f"Total disk IO: {io_count}")
randomBKeys = random.sample(relationAB.refKeys, 20)
for tuple in joinResults:
    key, valR1, valR2 = tuple
    if key in randomBKeys:
        print(key, valR1, valR2)

joinResults, io_count = hashJoin(mem, disk, relationBC, relationAB2)
verifyHashJoin(joinResults, relationBC, relationAB2)
print(f"Disk IO (BC buckets pre-computed): {io_count} \nTotal Disk IO: {io_count + relationBC.metrics[0]}")
for tuple in joinResults:
    key, valR1, valR2 = tuple
    print(key, valR1, valR2)


'''
Doubts:
1. Disk IO for AB2. BC buckets are already computed in disk for previous BC-AB join. So, should we count them again?
2. Randomly picking B keys for printing join results, should I pick existing B keys from AB ((20 tuples) or any B is fine? 
'''