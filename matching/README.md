# Matching

This module compute unique_id which input feature belongs to.
Use feature to compare directly.

## Getting Started

### Prerequisites

1. Python 2.7
2. numpy

### Installing

1. install numpy  
    ```bash
    sudo pip2 install numpy
    ```
1. checkout project  
    ```bash
    git clone http://yicun.vmaxx.tech:3000/hyliu/matching.git  
    cd matching/
    ```

**for python 3.x users**  
currently not support

## How to use

### Example

```python
mm = MatchingModule(mm_cfg)
mm.register(input_feature)
mm.match(input_feature)
mm.free()
```

for further usage please refer to [sample_random_testdata.py](sample_random_testdata.py)

### Supported matching method

1. Cosine distance  
1. Euclidean distance  

## Version

for time consuming information please refer to [process_time_report.xlsx](doc/process_time_report.xlsx)

### 1.4.0

1. new interface

### 1.3.2

1. add version info
1. fix empty register bug

#### issue

1. json takes time seriously

### 1.3.1

1. optimize numpy append feature

### 1.3.0

1. add numpy matrix operation

## TODO LIST

### Optimize

1. Falconn can speed up register process
1. multiprocess
1. hnsw
1. flann

### Question
