import numpy as np
from gmac import gmac, GF2p128, Polynomial
from tqdm import trange

def block2gf(block):
    assert len(block) == 16
    return GF2p128(int.from_bytes(block, 'big'))

def gf2vec(val: GF2p128):
    ret = np.empty((128,), dtype=np.uint8)
    val = val.val
    for i in range(128):
        ret[i] = val & 1
        val >>= 1
    return ret

sqr_mat = np.empty((128, 128), dtype=np.uint8)
for i in range(128):
    sqr_mat[:, i] = gf2vec(GF2p128(1 << i) ** 2)

def gf2mat(val: GF2p128):
    ret = np.empty((128, 128), dtype=np.uint8)
    acc = GF2p128(1)
    for i in range(128):
        ret[:, i] = gf2vec(val * acc)
        acc.val <<= 1
    return ret

def vec2gf(vec: np.array):
    ret = 0
    for bit in reversed(vec):
        ret <<= 1
        ret |= int(bit)
    return GF2p128(ret)

test = block2gf(b"One day I'm gon'")
assert (gf2vec(test ** 2) == (sqr_mat @ gf2vec(test)) % 2).all()
test2 = block2gf(b'marry a pornstar')
assert (gf2vec(test * test2) == (gf2mat(test2) @ gf2vec(test)) % 2).all()

def get_Ad(blocks):
    # starting from ^2 since ^1 is the section length
    power = sqr_mat @ sqr_mat
    acc = np.zeros((128, 128), dtype=np.uint8)
    for block in blocks:
        acc = (gf2mat(block2gf(block)) @ power + acc) % 2
        power = (power @ sqr_mat) % 2
    return acc

def get_Ad_loc(i):
    block_idx = i // 128
    cell_idx = i % 128
    byte_idx = cell_idx // 8
    bit_idx = cell_idx % 8
    payload = [bytes(16)] * (1 + block_idx) + \
                [bytes(byte_idx) + bytes([1 << bit_idx]) + bytes(15 - byte_idx)] + \
                [bytes(16)] * (127 - block_idx)
    return get_Ad(payload)

n = 16
Ad_0 = get_Ad([b'\x00' * 16] * (n + 1))
# rows = bits in Ad, col = bits in blocks
dependency = np.empty(((n - 1) * 128, n * 128), dtype=np.uint8)
for bit_idx in trange(n * 128):
    mat = get_Ad_loc(bit_idx)
    shape = mat.shape
    for i in range(1, n):
        for j in range(shape[1]):
            dependency[i * 128 + j - 128, bit_idx] = int(mat[i][j] == Ad_0[i][j])

print(dependency)