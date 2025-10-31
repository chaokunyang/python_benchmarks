# Python Benchmark

Microbenchmark comparing Apache Fory™ and Dill/Dill serialization performance in CPython.

This benchmark is derived from https://github.com/apache/fory/tree/main/integration_tests/cpython_benchmark

## Benchmark Result

- **System Information**: Details about the hardware and OS where benchmarks were run (useful for comparing results across different machines)
- **Mean**: Average time per serialization+deserialization cycle
- **Std Dev**: Standard deviation of the measurements
- **Size**: Byte size of the serialized data
- **Speedup**: How many times faster Fory is compared to Dill (higher is better for Fory)
- **Ratio**: Size ratio (Dill/Fory). Values > 1.0 mean Fory produces more compact output


```
================================================================================
SYSTEM INFORMATION
================================================================================
OS                        Darwin 24.5.0
Machine                   arm64
Processor                 arm
CPU Cores (Physical)      12
CPU Cores (Logical)       12
Total RAM (GB)            48.0
================================================================================

Benchmarking 10 benchmark(s) with 2 serializer(s)
Warmup: 3, Iterations: 20, Repeat: 5, Inner loop: 100
Fory reference tracking: enabled
================================================================================

Running fory_dict... 3.65 us ± 332.87 ns
Running dill_dict... 79.43 us ± 1.66 us

Running fory_large_dict... 25.57 us ± 563.11 ns
Running dill_large_dict... 779.05 us ± 22.07 us

Running fory_dict_group... 7.68 us ± 581.16 ns
Running dill_dict_group... 167.81 us ± 2.88 us

Running fory_tuple... 1.02 us ± 255.73 ns
Running dill_tuple... 19.01 us ± 512.41 ns

Running fory_large_tuple... 7.30 us ± 378.65 ns
Running dill_large_tuple... 289.23 us ± 8.73 us

Running fory_large_float_tuple... 6.16 us ± 266.92 ns
Running dill_large_float_tuple... 285.81 us ± 80.61 us

Running fory_large_boolean_tuple... 4.93 us ± 283.80 ns
Running dill_large_boolean_tuple... 259.09 us ± 4.14 us

Running fory_list... 4.97 us ± 380.88 ns
Running dill_list... 154.16 us ± 12.94 us

Running fory_large_list... 7.29 us ± 425.87 ns
Running dill_large_list... 293.88 us ± 3.56 us

Running fory_complex... 2.47 us ± 255.68 ns
Running dill_complex... 1.66 ms ± 37.13 us

================================================================================
SUMMARY
================================================================================
Serializer      Benchmark                 Mean                 Std Dev             
--------------------------------------------------------------------------------
fory            dict                      3.65 us              332.87 ns           
dill            dict                      79.43 us             1.66 us             
fory            large_dict                25.57 us             563.11 ns           
dill            large_dict                779.05 us            22.07 us            
fory            dict_group                7.68 us              581.16 ns           
dill            dict_group                167.81 us            2.88 us             
fory            tuple                     1.02 us              255.73 ns           
dill            tuple                     19.01 us             512.41 ns           
fory            large_tuple               7.30 us              378.65 ns           
dill            large_tuple               289.23 us            8.73 us             
fory            large_float_tuple         6.16 us              266.92 ns           
dill            large_float_tuple         285.81 us            80.61 us            
fory            large_boolean_tuple       4.93 us              283.80 ns           
dill            large_boolean_tuple       259.09 us            4.14 us             
fory            list                      4.97 us              380.88 ns           
dill            list                      154.16 us            12.94 us            
fory            large_list                7.29 us              425.87 ns           
dill            large_list                293.88 us            3.56 us             
fory            complex                   2.47 us              255.68 ns           
dill            complex                   1.66 ms              37.13 us            

================================================================================
SERIALIZED SIZE COMPARISON
================================================================================
Serializer      Benchmark                 Size                
--------------------------------------------------------------------------------
fory            dict                      607 B               
dill            dict                      683 B               
fory            large_dict                2.85 KB             
dill            large_dict                4.17 KB             
fory            dict_group                3.26 KB             
dill            dict_group                2.92 KB             
fory            tuple                     112 B               
dill            tuple                     120 B               
fory            large_tuple               969 B               
dill            large_tuple               1.27 KB             
fory            large_float_tuple         4.01 KB             
dill            large_float_tuple         4.52 KB             
fory            large_boolean_tuple       4.01 KB             
dill            large_boolean_tuple       528 B               
fory            list                      326 B               
dill            list                      536 B               
fory            large_list                969 B               
dill            large_list                1.27 KB             
fory            complex                   89 B                
dill            complex                   8.37 KB             

================================================================================
SPEEDUP (Fory vs Dill)
================================================================================
Benchmark                 Fory                 Dill                 Speedup             
--------------------------------------------------------------------------------
dict                      3.65 us              79.43 us             21.77x              
large_dict                25.57 us             779.05 us            30.46x              
dict_group                7.68 us              167.81 us            21.86x              
tuple                     1.02 us              19.01 us             18.71x              
large_tuple               7.30 us              289.23 us            39.64x              
large_float_tuple         6.16 us              285.81 us            46.41x              
large_boolean_tuple       4.93 us              259.09 us            52.53x              
list                      4.97 us              154.16 us            30.99x              
large_list                7.29 us              293.88 us            40.29x              
complex                   2.47 us              1.66 ms              672.08x             

================================================================================
SIZE COMPARISON (Fory vs Dill)
================================================================================
Benchmark                 Fory                 Dill                 Ratio               
--------------------------------------------------------------------------------
dict                      607 B                683 B                1.13x               
large_dict                2.85 KB              4.17 KB              1.46x               
dict_group                3.26 KB              2.92 KB              1.12x larger        
tuple                     112 B                120 B                1.07x               
large_tuple               969 B                1.27 KB              1.34x               
large_float_tuple         4.01 KB              4.52 KB              1.13x               
large_boolean_tuple       4.01 KB              528 B                7.79x larger        
list                      326 B                536 B                1.64x               
large_list                969 B                1.27 KB              1.34x               
complex                   89 B                 8.37 KB              96.34x    
```

## Quick Start for reproduction

```bash
pip install pyfory dill psutil
python benchmark.py
```

This will run all benchmarks with both Fory and Dill serializers using default settings.

## Usage

### Basic Usage

```bash
# Run all benchmarks with both Fory and Dill
python benchmark.py

# Run all benchmarks without reference tracking
python benchmark.py --no-ref

# Run specific benchmarks
python benchmark.py --benchmarks dict,large_dict,complex

# Compare only Fory performance
python benchmark.py --serializers fory

# Compare only Dill performance
python benchmark.py --serializers dill

# Run with more iterations for better accuracy
python benchmark.py --iterations 50 --repeat 10

# Debug with pure Python mode
python benchmark.py --disable-cython --benchmarks dict
```

## Command-Line Options

### Benchmark Selection

#### `--benchmarks BENCHMARK_LIST`

Comma-separated list of benchmarks to run. Default: `all`

Available benchmarks:

- `dict` - Small dictionary serialization (28 fields with mixed types)
- `large_dict` - Large dictionary (2^9 + 1 entries)
- `dict_group` - Group of 3 dictionaries
- `tuple` - Small tuple with nested list
- `large_tuple` - Large tuple (2^9 + 1 integers)
- `large_float_tuple` - Large tuple of floats (2^9 + 1 elements)
- `large_boolean_tuple` - Large tuple of booleans (2^9 + 1 elements)
- `list` - Nested lists (10x10x10 structure)
- `large_list` - Large list (2^9 + 1 integers)
- `complex` - Complex dataclass objects with nested structures

Examples:

```bash
# Run only dictionary benchmarks
python benchmark.py --benchmarks dict,large_dict,dict_group

# Run only large data benchmarks
python benchmark.py --benchmarks large_dict,large_tuple,large_list

# Run only the complex object benchmark
python benchmark.py --benchmarks complex
```

#### `--serializers SERIALIZER_LIST`

Comma-separated list of serializers to benchmark. Default: `all`

Available serializers:

- `fory` - Apache Fory™ serialization
- `dill` - Python's built-in dill serialization

Examples:

```bash
# Compare both serializers (default)
python benchmark.py --serializers fory,dill

# Benchmark only Fory
python benchmark.py --serializers fory

# Benchmark only Dill
python benchmark.py --serializers dill
```

### Configuration

#### `--no-ref`

Disable reference tracking for Fory. By default, Fory tracks references to handle shared and circular references.

```bash
# Run without reference tracking
python benchmark.py --no-ref
```

### Benchmark Parameters

These options control the benchmark measurement process:

#### `--warmup N`

Number of warmup iterations before measurement starts. Default: `3`

```bash
python benchmark.py --warmup 5
```

#### `--iterations N`

Number of measurement iterations to collect. Default: `20`

```bash
python benchmark.py --iterations 50
```

#### `--repeat N`

Number of times to repeat each iteration. Default: `5`

```bash
python benchmark.py --repeat 10
```

#### `--number N`

Number of times to call the serialization function per measurement (inner loop). Default: `100`

```bash
python benchmark.py --number 1000
```

#### `--help`

Display help message and exit.

```bash
python benchmark.py --help
```

## Examples

### Running Specific Comparisons

```bash
# Compare Fory and Dill on dictionary benchmarks
python benchmark.py --benchmarks dict,large_dict,dict_group

# Compare performance without reference tracking
python benchmark.py --no-ref

# Test only Fory with high precision
python benchmark.py --serializers fory --iterations 100 --repeat 10
```

### Performance Tuning

```bash
# Quick test with fewer iterations
python benchmark.py --warmup 1 --iterations 5 --repeat 3

# High-precision benchmark
python benchmark.py --warmup 10 --iterations 100 --repeat 10

# Benchmark large data structures with more inner loop iterations
python benchmark.py --benchmarks large_list,large_tuple --number 1000
```

### Debugging and Development

```bash
# Test complex objects only
python benchmark.py --benchmarks complex --iterations 10

# Compare Fory with and without ref tracking
python benchmark.py --serializers fory --benchmarks dict
python benchmark.py --serializers fory --benchmarks dict --no-ref

# Analyze size differences for large data structures
python benchmark.py --benchmarks large_dict,large_list --serializers fory,dill
```
