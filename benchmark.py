# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Apache Fory™ vs Dill CPython Benchmark Suite

Microbenchmark comparing Apache Fory™ and Dill serialization performance in CPython.

Usage:
    python benchmark.py [OPTIONS]

Benchmark Options:
    --benchmarks BENCHMARK_LIST
        Comma-separated list of benchmarks to run. Default: all
        Available: dict, large_dict, dict_group, tuple, large_tuple,
                   large_float_tuple, large_boolean_tuple, list, large_list, complex

    --serializers SERIALIZER_LIST
        Comma-separated list of serializers to benchmark. Default: all
        Available: fory, dill
        Example: --serializers fory,dill

    --no-ref
        Disable reference tracking for Fory (enabled by default)

    --warmup N
        Number of warmup iterations (default: 3)

    --iterations N
        Number of benchmark iterations (default: 20)

    --repeat N
        Number of times to repeat each iteration (default: 5)

    --number N
        Number of times to call function per measurement (inner loop, default: 100)

    --help
        Show help message and exit

Examples:
    # Run all benchmarks with both Fory and Dill
    python benchmark.py

    # Run specific benchmarks with both serializers
    python benchmark.py --benchmarks dict,large_dict,complex

    # Compare only Fory performance
    python benchmark.py --serializers fory

    # Compare only Dill performance
    python benchmark.py --serializers dill

    # Run without reference tracking for Fory
    python benchmark.py --no-ref

    # Run with more iterations for better accuracy
    python benchmark.py --iterations 50 --repeat 10
"""

import argparse
from dataclasses import dataclass
import datetime
import dill as dill
import random
import statistics
import sys
import timeit
from typing import Any, Dict, List
import pyfory
import platform
import psutil


# The benchmark case is rewritten from pyperformance bm_dill
# https://github.com/python/pyperformance/blob/main/pyperformance/data-files/benchmarks/bm_dill/run_benchmark.py
DICT = {
    "ads_flags": 0,
    "age": 18,
    "birthday": datetime.date(1980, 5, 7),
    "bulletin_count": 0,
    "comment_count": 0,
    "country": "BR",
    "encrypted_id": "G9urXXAJwjE",
    "favorite_count": 9,
    "first_name": "",
    "flags": 412317970704,
    "friend_count": 0,
    "gender": "m",
    "gender_for_display": "Male",
    "id": 302935349,
    "is_custom_profile_icon": 0,
    "last_name": "",
    "locale_preference": "pt_BR",
    "member": 0,
    "tags": ["a", "b", "c", "d", "e", "f", "g"],
    "profile_foo_id": 827119638,
    "secure_encrypted_id": "Z_xxx2dYx3t4YAdnmfgyKw",
    "session_number": 2,
    "signup_id": "201-19225-223",
    "status": "A",
    "theme": 1,
    "time_created": 1225237014,
    "time_updated": 1233134493,
    "unread_message_count": 0,
    "user_group": "0",
    "username": "collinwinter",
    "play_count": 9,
    "view_count": 7,
    "zip": "",
}
LARGE_DICT = {str(i): i for i in range(2**9 + 1)}

TUPLE = (
    [
        265867233,
        265868503,
        265252341,
        265243910,
        265879514,
        266219766,
        266021701,
        265843726,
        265592821,
        265246784,
        265853180,
        45526486,
        265463699,
        265848143,
        265863062,
        265392591,
        265877490,
        265823665,
        265828884,
        265753032,
    ],
    60,
)
LARGE_TUPLE = tuple(range(2**9 + 1))
LARGE_FLOAT_TUPLE = tuple([random.random() * 10000 for _ in range(2**9 + 1)])
LARGE_BOOLEAN_TUPLE = tuple([bool(random.random() > 0.5) for _ in range(2**9 + 1)])


LIST = [[list(range(10)), list(range(10))] for _ in range(10)]
LARGE_LIST = [i for i in range(2**9 + 1)]


def mutate_dict(orig_dict, random_source):
    new_dict = dict(orig_dict)
    for key, value in new_dict.items():
        rand_val = random_source.random() * sys.maxsize
        if isinstance(key, (int, bytes, str)):
            new_dict[key] = type(key)(rand_val)
    return new_dict


random_source = random.Random(5)
DICT_GROUP = [mutate_dict(DICT, random_source) for _ in range(3)]


@dataclass
class ComplexObject1:
    f1: Any = None
    f2: str = None
    f3: List[str] = None
    f4: Dict[pyfory.int8, pyfory.int32] = None
    f5: pyfory.int8 = None
    f6: pyfory.int16 = None
    f7: pyfory.int32 = None
    f8: pyfory.int64 = None
    f9: pyfory.float32 = None
    f10: pyfory.float64 = None
    f11: pyfory.int16_array = None
    f12: List[pyfory.int16] = None


@dataclass
class ComplexObject2:
    f1: Any
    f2: Dict[pyfory.int8, pyfory.int32]


COMPLEX_OBJECT = ComplexObject1(
    f1=ComplexObject2(f1=True, f2={-1: 2}),
    f2="abc",
    f3=["abc", "abc"],
    f4={1: 2},
    f5=2**7 - 1,
    f6=2**15 - 1,
    f7=2**31 - 1,
    f8=2**63 - 1,
    f9=1.0 / 2,
    f10=1 / 3.0,
    f11=[-1, 4],
)

# Global fory instances
fory_with_ref = pyfory.Fory(ref=True)
fory_without_ref = pyfory.Fory(ref=False)

# Register all custom types on both instances
for fory_instance in (fory_with_ref, fory_without_ref):
    fory_instance.register_type(ComplexObject1)
    fory_instance.register_type(ComplexObject2)


def fory_object(ref, obj):
    fory = fory_with_ref if ref else fory_without_ref
    binary = fory.serialize(obj)
    fory.deserialize(binary)


def fory_data_class(ref, obj):
    fory = fory_with_ref if ref else fory_without_ref
    binary = fory.serialize(obj)
    fory.deserialize(binary)


def dill_object(obj):
    binary = dill.dumps(obj)
    dill.loads(binary)


def dill_data_class(obj):
    binary = dill.dumps(obj)
    dill.loads(binary)


def benchmark_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Fory vs Dill Benchmark")
    parser.add_argument(
        "--no-ref",
        action="store_true",
        default=False,
        help="Disable reference tracking for Fory",
    )
    parser.add_argument(
        "--benchmarks",
        type=str,
        default="all",
        help="Comma-separated list of benchmarks to run. Available: dict, large_dict, "
        "dict_group, tuple, large_tuple, large_float_tuple, large_boolean_tuple, "
        "list, large_list, complex. Default: all",
    )
    parser.add_argument(
        "--serializers",
        type=str,
        default="all",
        help="Comma-separated list of serializers to benchmark. Available: fory, dill. Default: all",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=3,
        help="Number of warmup iterations (default: 3)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=20,
        help="Number of benchmark iterations (default: 20)",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=5,
        help="Number of times to repeat each iteration (default: 5)",
    )
    parser.add_argument(
        "--number",
        type=int,
        default=100,
        help="Number of times to call function per measurement (inner loop, default: 10000)",
    )
    return parser.parse_args()


def run_benchmark(func, *args, warmup=3, iterations=20, repeat=5, number=10000):
    """Run a benchmark and return timing statistics

    Args:
        func: Function to benchmark
        *args: Arguments to pass to func
        warmup: Number of warmup iterations
        iterations: Number of measurement iterations
        repeat: Number of times to repeat each measurement
        number: Number of times to call func per measurement (inner loop)

    Returns:
        (mean_time_per_call, stdev_time_per_call)
    """
    # Warmup
    for _ in range(warmup):
        for _ in range(number):
            func(*args)

    # Benchmark - run func 'number' times per measurement
    times = []
    for _ in range(iterations):
        timer = timeit.Timer(lambda: func(*args))
        iteration_times = timer.repeat(repeat=repeat, number=number)
        # Convert total time to time per call
        times.extend([t / number for t in iteration_times])

    mean = statistics.mean(times)
    stdev = statistics.stdev(times) if len(times) > 1 else 0
    return mean, stdev


def get_serialized_size(serializer, ref, obj):
    """Get the size of serialized data in bytes

    Args:
        serializer: "fory" or "dill"
        ref: Whether reference tracking is enabled (for fory only)
        obj: Object to serialize

    Returns:
        Size in bytes
    """
    if serializer == "fory":
        fory = fory_with_ref if ref else fory_without_ref
        binary = fory.serialize(obj)
        return len(binary)
    else:  # dill
        binary = dill.dumps(obj)
        return len(binary)


def format_time(seconds):
    """Format time in human-readable units"""
    if seconds < 1e-6:
        return f"{seconds * 1e9:.2f} ns"
    elif seconds < 1e-3:
        return f"{seconds * 1e6:.2f} us"
    elif seconds < 1:
        return f"{seconds * 1e3:.2f} ms"
    else:
        return f"{seconds:.2f} s"


def format_size(bytes_size):
    """Format size in human-readable units"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.2f} KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes_size / (1024 * 1024 * 1024):.2f} GB"


def get_system_info():
    try:
        info = {
            "OS": f"{platform.system()} {platform.release()}",
            "Machine": platform.machine(),
            "Processor": platform.processor() or "Unknown",
            "CPU Cores (Physical)": psutil.cpu_count(logical=False),
            "CPU Cores (Logical)": psutil.cpu_count(logical=True),
            "Total RAM (GB)": round(psutil.virtual_memory().total / (1024**3), 2),
        }
    except Exception as e:
        info = {"Error gathering system info": str(e)}
    return info



def micro_benchmark():
    args = benchmark_args()
    ref = not args.no_ref

    # Print system information
    system_info = get_system_info()
    print("\n" + "=" * 80)
    print("SYSTEM INFORMATION")
    print("=" * 80)
    for key, value in system_info.items():
        print(f"{key:<25} {value}")
    print("=" * 80)

    # Define benchmark data and functions
    benchmark_data = {
        "dict": (DICT, fory_object, dill_object),
        "large_dict": (LARGE_DICT, fory_object, dill_object),
        "dict_group": (DICT_GROUP, fory_object, dill_object),
        "tuple": (TUPLE, fory_object, dill_object),
        "large_tuple": (LARGE_TUPLE, fory_object, dill_object),
        "large_float_tuple": (LARGE_FLOAT_TUPLE, fory_object, dill_object),
        "large_boolean_tuple": (LARGE_BOOLEAN_TUPLE, fory_object, dill_object),
        "list": (LIST, fory_object, dill_object),
        "large_list": (LARGE_LIST, fory_object, dill_object),
        "complex": (COMPLEX_OBJECT, fory_data_class, dill_data_class),
    }

    # Determine which benchmarks to run
    if args.benchmarks == "all":
        selected_benchmarks = list(benchmark_data.keys())
    else:
        selected_benchmarks = [b.strip() for b in args.benchmarks.split(",")]
        # Validate benchmark names
        invalid = [b for b in selected_benchmarks if b not in benchmark_data]
        if invalid:
            print(f"Error: Invalid benchmark names: {', '.join(invalid)}")
            print(f"Available benchmarks: {', '.join(benchmark_data.keys())}")
            sys.exit(1)

    # Determine which serializers to run
    available_serializers = {"fory", "dill"}
    if args.serializers == "all":
        selected_serializers = ["fory", "dill"]
    else:
        selected_serializers = [s.strip() for s in args.serializers.split(",")]
        # Validate serializer names
        invalid = [s for s in selected_serializers if s not in available_serializers]
        if invalid:
            print(f"Error: Invalid serializer names: {', '.join(invalid)}")
            print(f"Available serializers: {', '.join(available_serializers)}")
            sys.exit(1)

    print(
        f"\nBenchmarking {len(selected_benchmarks)} benchmark(s) with {len(selected_serializers)} serializer(s)"
    )
    print(
        f"Warmup: {args.warmup}, Iterations: {args.iterations}, Repeat: {args.repeat}, Inner loop: {args.number}"
    )
    print(f"Fory reference tracking: {'enabled' if ref else 'disabled'}")
    print("=" * 80)

    # Run selected benchmarks with selected serializers
    results = []
    sizes = []
    for benchmark_name in selected_benchmarks:
        data, fory_func, dill_func = benchmark_data[benchmark_name]

        if "fory" in selected_serializers:
            print(f"\nRunning fory_{benchmark_name}...", end=" ", flush=True)
            mean, stdev = run_benchmark(
                fory_func,
                ref,
                data,
                warmup=args.warmup,
                iterations=args.iterations,
                repeat=args.repeat,
                number=args.number,
            )
            size = get_serialized_size("fory", ref, data)
            results.append(("fory", benchmark_name, mean, stdev))
            sizes.append(("fory", benchmark_name, size))
            print(f"{format_time(mean)} ± {format_time(stdev)}")

        if "dill" in selected_serializers:
            print(f"Running dill_{benchmark_name}...", end=" ", flush=True)
            mean, stdev = run_benchmark(
                dill_func,
                data,
                warmup=args.warmup,
                iterations=args.iterations,
                repeat=args.repeat,
                number=args.number,
            )
            size = get_serialized_size("dill", ref, data)
            results.append(("dill", benchmark_name, mean, stdev))
            sizes.append(("dill", benchmark_name, size))
            print(f"{format_time(mean)} ± {format_time(stdev)}")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"{'Serializer':<15} {'Benchmark':<25} {'Mean':<20} {'Std Dev':<20}")
    print("-" * 80)
    for serializer, benchmark, mean, stdev in results:
        print(
            f"{serializer:<15} {benchmark:<25} {format_time(mean):<20} {format_time(stdev):<20}"
        )

    # Print serialized size comparison
    if sizes:
        print("\n" + "=" * 80)
        print("SERIALIZED SIZE COMPARISON")
        print("=" * 80)
        print(f"{'Serializer':<15} {'Benchmark':<25} {'Size':<20}")
        print("-" * 80)
        for serializer, benchmark, size in sizes:
            print(
                f"{serializer:<15} {benchmark:<25} {format_size(size):<20}"
            )

    # Calculate speedup if both serializers were tested
    if "fory" in selected_serializers and "dill" in selected_serializers:
        print("\n" + "=" * 80)
        print("SPEEDUP (Fory vs Dill)")
        print("=" * 80)
        print(f"{'Benchmark':<25} {'Fory':<20} {'Dill':<20} {'Speedup':<20}")
        print("-" * 80)

        for benchmark_name in selected_benchmarks:
            fory_result = next(
                (r for r in results if r[0] == "fory" and r[1] == benchmark_name), None
            )
            dill_result = next(
                (r for r in results if r[0] == "dill" and r[1] == benchmark_name),
                None,
            )

            if fory_result and dill_result:
                fory_mean = fory_result[2]
                dill_mean = dill_result[2]
                speedup = dill_mean / fory_mean
                speedup_str = (
                    f"{speedup:.2f}x" if speedup >= 1 else f"{1 / speedup:.2f}x slower"
                )
                print(
                    f"{benchmark_name:<25} {format_time(fory_mean):<20} {format_time(dill_mean):<20} {speedup_str:<20}"
                )

        # Size comparison table
        print("\n" + "=" * 80)
        print("SIZE COMPARISON (Fory vs Dill)")
        print("=" * 80)
        print(f"{'Benchmark':<25} {'Fory':<20} {'Dill':<20} {'Ratio':<20}")
        print("-" * 80)

        for benchmark_name in selected_benchmarks:
            fory_size = next(
                (s for s in sizes if s[0] == "fory" and s[1] == benchmark_name), None
            )
            dill_size = next(
                (s for s in sizes if s[0] == "dill" and s[1] == benchmark_name), None
            )

            if fory_size and dill_size:
                fory_bytes = fory_size[2]
                dill_bytes = dill_size[2]
                ratio = dill_bytes / fory_bytes if fory_bytes > 0 else float('inf')
                ratio_str = (
                    f"{ratio:.2f}x" if ratio >= 1 else f"{1 / ratio:.2f}x larger"
                )
                print(
                    f"{benchmark_name:<25} {format_size(fory_bytes):<20} {format_size(dill_bytes):<20} {ratio_str:<20}"
                )


if __name__ == "__main__":
    micro_benchmark()
