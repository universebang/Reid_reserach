import numpy as np
import timeit
import math
import json


def euclidean_distance(register_feature, feature):
    # return np.linalg.norm((np.array(f1) - np.array(f2)))
    ff = np.tile(feature, register_feature.shape[0])
    ff = np.reshape(ff, (register_feature.shape[0], register_feature.shape[1]))
    diff = register_feature - ff
    return np.linalg.norm(np.dot(diff, diff.T), axis=1)


def cosine_distance(register_feature, norm_feature):
    dot = np.dot(register_feature, norm_feature)
    return np.ones(shape=dot.shape) - dot


def gen_near_neighbor(v, r):
    rp = np.random.randn(v.size)
    rp = rp / np.linalg.norm(rp)
    rp = rp - np.dot(rp, v) * v
    rp = rp / np.linalg.norm(rp)
    alpha = 1 - r * r / 2.0
    beta = math.sqrt(1.0 - alpha * alpha)
    return alpha * v + beta * rp


def aligned(a, alignment=32):
    if (a.ctypes.data % alignment) == 0:
        return a
    extra = alignment // a.itemsize
    buf = np.empty(a.size + extra, dtype=a.dtype)
    ofs = (-buf.ctypes.data % alignment) // a.itemsize
    aa = buf[ofs:ofs + a.size].reshape(a.shape)
    np.copyto(aa, a)
    assert (aa.ctypes.data % alignment) == 0
    return aa


def generate_data(num_index, dim, seed):
    print 'Generating data set ...', num_index, dim
    np.random.seed(seed)
    data = np.random.randn(num_index, dim)
    norms = np.linalg.norm(data, axis=1)
    data = data / np.reshape(norms, (num_index, 1))
    data = data.astype(np.float32)
    data = aligned(data)
    return data


def generate_queries(num_queries, data, radius, num_index):
    print 'Generating queries ...', num_queries
    queries = []
    nn = []
    for ii in range(num_queries):
        n = np.random.randint(num_index)
        q = gen_near_neighbor(data[n], radius)
        q = aligned(q)
        queries.append(q.astype(np.float32))
        nn.append(n)
    return queries, nn


def calculate(data, queries):
    print('Computing true nearest neighbors via a linear scan ...')
    true_nns = []
    average_scan_time = 0.0

    for query in queries:
        start = timeit.default_timer()
        # dot = np.dot(data, query)
        dot = cosine_distance(data, query)
        best_index = np.argmin(dot)
        # print np.sort(dot), best_index
        stop = timeit.default_timer()
        true_nns.append(best_index)
        average_scan_time += (stop - start)
    average_scan_time /= num_queries
    print('Average query time: {} seconds'.format(average_scan_time))
    return true_nns


n = 20
d = 512
num_queries = 5
r = math.sqrt(2.0) / 2.0
seed = 119417657

data = generate_data(n, d, seed)
queries, true_nns = generate_queries(num_queries, data, r, n)
calc_nns = calculate(data, queries)
do_one = np.dot(queries, np.transpose(data))

precision = 0
for i, t in enumerate(true_nns):
    if t == calc_nns[i]:
        precision += 1
    print t, np.argmax(do_one[i])
print 'precision = ', precision * 100.0 / len(true_nns), '%'

key = [x for x in range(n)]
data_list = []
for da in data.tolist():
    data_list.append([da])
with open("register.json", "w") as file:
    json.dump(dict(zip(key, data_list)), file, indent=4)

result_dict = {}
for t in true_nns:
    result_dict[t] = []
for t, q in enumerate(queries):
    result_dict[true_nns[t]].append(q.tolist())

with open("matching.json", "w") as file:
    json.dump(result_dict, file, indent=4)
