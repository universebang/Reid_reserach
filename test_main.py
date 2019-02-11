from numpy import random
import pykgraph
import numpy as np
dataset = random.rand(100, 16)
print(type(dataset))
buf = [0 for x in range(10)]
query = [dataset[i] for i in buf]
query=np.array(query)
index = pykgraph.KGraph(dataset, 'euclidean')  # another option is 'angular'
index.build(reverse=-1)                        #
#index.save("index_file")
# load with index.load("index_file");

knn = index.search(query, K=1)
print(type(knn))
print(knn)