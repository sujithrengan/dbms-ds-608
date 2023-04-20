import random, string, math

class Relation:
    def __init__(self, name, base_address, size=0, ref = [], refKeys = set()):
        self.name = name
        self.base_address = base_address
        self.size = size
        self.ref = ref
        self.refKeys = refKeys

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
        self.array = [None] * self.BUCKET_CAP * 200
        self.cursor = 0

    def readBlock(self, block_id):
        return self.array[block_id]

    def writeBlockSeq(self, block):
        self.array[self.cursor] = block
        self.cursor += 1
    
    def writeBlock(self, block, block_id):
        self.array[block_id] = block
    
    def getWriteCursor(self):
        return self.cursor
    
class VirtualMemory:
    def __init__(self):
        self.SIZE = 15
        self.array = [None] * self.SIZE * 8
        self.base_address = 8 # First 8 blocks are reserved for metadata

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
    return Relation("AB2", base_address, size, ref, refKeys)

def jenkinsHash(key, size):
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

def generateBuckets(mem, disk, R, num_buckets):
    r = 0 if R.name == "BC" else 1
    mem.array[r] = [0] * num_buckets
    for i in range(R.size//disk.BLOCK_SIZE):
        mem.readFromDisk(disk, R.base_address + i , mem.base_address)
        bucket_base = mem.base_address + disk.BLOCK_SIZE
        for j in range(mem.base_address, mem.base_address + disk.BLOCK_SIZE):
            key, val = mem.array[j]
            hash = jenkinsHash(key, num_buckets)
            # print(hash, mem.base_address + hash * disk.BLOCK_SIZE + mem.array[r][hash], len(mem.array))
            mem.array[bucket_base + hash * disk.BLOCK_SIZE + mem.array[r][hash]%disk.BLOCK_SIZE] = (key, val)
            mem.array[r][hash] += 1
            if mem.array[r][hash]%disk.BLOCK_SIZE == 0:
                # print("Full: ", hash, mem.array[r][hash], disk.cursor + hash * disk.BUCKET_CAP + mem.array[r][hash]//disk.BLOCK_SIZE, mem.base_address + hash * disk.BLOCK_SIZE, mem.array[bucket_base + hash * disk.BLOCK_SIZE:bucket_base + hash * disk.BLOCK_SIZE + disk.BLOCK_SIZE])
                mem.writeToDiskLoc(disk, disk.cursor + hash * disk.BUCKET_CAP + mem.array[r][hash]//disk.BLOCK_SIZE - 1, bucket_base + hash * disk.BLOCK_SIZE)
                for i in range(disk.BLOCK_SIZE):
                    mem.array[bucket_base + hash * disk.BLOCK_SIZE + i] = None
    for bucket in range(num_buckets):
        if mem.array[r][bucket]%disk.BLOCK_SIZE > 0:
            print(bucket, 
                  mem.array[r][bucket]%disk.BLOCK_SIZE, 
                  disk.cursor + bucket*disk.BUCKET_CAP + mem.array[r][bucket]//disk.BLOCK_SIZE, 
                  mem.base_address + bucket * disk.BLOCK_SIZE, 
                  mem.array[bucket_base + bucket * disk.BLOCK_SIZE:bucket_base + bucket * disk.BLOCK_SIZE + disk.BLOCK_SIZE])
            mem.writeToDiskLoc(disk, disk.cursor + bucket * disk.BUCKET_CAP + mem.array[r][bucket]//disk.BLOCK_SIZE, bucket_base + bucket * disk.BLOCK_SIZE)
    
    disk.cursor += num_buckets * disk.BUCKET_CAP
    mem.flush()
    print("Buckets generated. disk.cursor=", disk.cursor)


def hashJoin(mem, disk, R1, R2):
    num_buckets = mem.SIZE - 2 # 1 block for reading, 1 for metadata
    generateBuckets(mem, disk, R1, num_buckets)
    generateBuckets(mem, disk, R2, num_buckets)

    disk.cursor -= 2 * num_buckets * disk.BUCKET_CAP

    joinResults = []
    for bucket in range(num_buckets):
        for i in range(math.ceil(mem.array[1][bucket]/disk.BLOCK_SIZE)):
            print(disk.array[disk.cursor + num_buckets * disk.BUCKET_CAP + bucket * disk.BUCKET_CAP + i])
            mem.readFromDisk(disk, disk.cursor + num_buckets * disk.BUCKET_CAP + bucket * disk.BUCKET_CAP + i, mem.base_address + (i+1)*disk.BLOCK_SIZE)
        # print(1, bucket, mem.array[mem.base_address + 8:mem.base_address + 8 + mem.array[1][bucket]])

        for j in range(math.ceil(mem.array[0][bucket]/disk.BLOCK_SIZE)):
            mem.readFromDisk(disk, disk.cursor + bucket * disk.BUCKET_CAP + j, mem.base_address)
            # print(0, bucket, mem.array[mem.base_address:mem.base_address + disk.BLOCK_SIZE])
            for tuple in mem.array[mem.base_address + 8:mem.base_address + 8 + mem.array[1][bucket]]:
                key1, val1 = tuple
                for l in range(disk.BLOCK_SIZE):
                    if mem.array[mem.base_address + l] == None:
                        break
                    key2, val2 = mem.array[mem.base_address + l]
                    if key1 == key2:
                        print(key1, val1, val2)
                        joinResults.append((key1, val1, val2))

    return joinResults

def testHashJoin(joinResults, R1, R2):
    for key, val1, val2 in joinResults:
        if (key, val2) not in R1.ref or (key, val1) not in R2.ref:
            print("Error:", key, val1, val2)
            return False
    print("Join verified")
    return True


random.seed(23)
disk = VirtualDisk()
mem = VirtualMemory()


relationBC = generateRelationBC(disk)
relationAB = generateRelationABFromBKeys(disk, relationBC.refKeys)
# relationAB2 = generateRelationAB(disk)

joinResults = hashJoin(mem, disk, relationBC, relationAB)
# print(joinResults)
testHashJoin(joinResults, relationBC, relationAB)





        