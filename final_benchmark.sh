#!/bin/bash

OUTPUT_DIR="./results"
DATA_FILE="$OUTPUT_DIR/benchmark_results.csv"

mkdir -p "$OUTPUT_DIR"

WINDOW_SIZE=5
TEST_SIZES=(128 256 512 1024)

echo "Type,Width,Height,Processes,Time(seconds),Throughput(Mpixels/s)" > "$DATA_FILE"

echo "==== Sequential Benchmarks ===="
for size in "${TEST_SIZES[@]}"; do
    echo "Sequential: ${size}x${size}"
    ./bin/median_sequential "$size" "$size" "$WINDOW_SIZE" 2>&1 | grep -E "(Elapsed|Pixels per)"
    RESULT_FILE="$OUTPUT_DIR/sequential_${size}x${size}_window${WINDOW_SIZE}.txt"
    if [ -f "$RESULT_FILE" ]; then
        EXEC_TIME=$(grep "Execution time" "$RESULT_FILE" | awk -F': ' '{print $2}' | awk '{print $1}')
        THROUGHPUT=$(grep "Throughput" "$RESULT_FILE" | awk -F': ' '{print $2}' | awk '{print $1}')
        echo "Sequential,${size},${size},1,${EXEC_TIME},${THROUGHPUT}" >> "$DATA_FILE"
    fi
done

echo ""
echo "==== Parallel Benchmarks (2 processes) ===="
for size in "${TEST_SIZES[@]}"; do
    echo "Parallel (2 procs): ${size}x${size}"
    mpirun -np 2 ./bin/median_parallel "$size" "$size" "$WINDOW_SIZE" 2>&1 | grep -E "(Elapsed|Pixels per)"
    RESULT_FILE="$OUTPUT_DIR/parallel_${size}x${size}_window${WINDOW_SIZE}_np2.txt"
    if [ -f "$RESULT_FILE" ]; then
        EXEC_TIME=$(grep "Execution time" "$RESULT_FILE" | awk -F': ' '{print $2}' | awk '{print $1}')
        THROUGHPUT=$(grep "Throughput" "$RESULT_FILE" | awk -F': ' '{print $2}' | awk '{print $1}')
        echo "Parallel,${size},${size},2,${EXEC_TIME},${THROUGHPUT}" >> "$DATA_FILE"
    fi
done

echo ""
echo "==== Benchmark Complete ===="
echo "Results:"
cat "$DATA_FILE"
