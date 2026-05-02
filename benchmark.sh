#!/bin/bash

# Benchmarking script for Median Filter

OUTPUT_DIR="./results"
DATA_FILE="$OUTPUT_DIR/benchmark_results.csv"

# Create results directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Clear previous results
> "$DATA_FILE"

echo "Median Filter Benchmarking Script"
echo "===================================="
echo ""

# Test configurations
WINDOW_SIZE=5
TEST_SIZES=(256 512 1024 2048)

# Add header to CSV
echo "Type,Width,Height,Processes,Time(seconds),Throughput(Mpixels/s)" > "$DATA_FILE"

echo "Starting sequential benchmarks..."
for size in "${TEST_SIZES[@]}"; do
    echo "Testing sequential: ${size}x${size}..."
    ./bin/median_sequential "$size" "$size" "$WINDOW_SIZE"
    
    # Parse the result and add to CSV
    RESULT_FILE="$OUTPUT_DIR/sequential_${size}x${size}_window${WINDOW_SIZE}.txt"
    if [ -f "$RESULT_FILE" ]; then
        EXEC_TIME=$(grep "Execution time" "$RESULT_FILE" | awk -F': ' '{print $2}' | awk '{print $1}')
        THROUGHPUT=$(grep "Throughput" "$RESULT_FILE" | awk -F': ' '{print $2}' | awk '{print $1}')
        echo "Sequential,${size},${size},1,${EXEC_TIME},${THROUGHPUT}" >> "$DATA_FILE"
    fi
done

echo ""
echo "Starting parallel benchmarks with 2 processes..."
for size in "${TEST_SIZES[@]}"; do
    echo "Testing parallel (2 procs): ${size}x${size}..."
    mpirun --oversubscribe -np 2 ./bin/median_parallel "$size" "$size" "$WINDOW_SIZE" 2>/dev/null
    
    RESULT_FILE="$OUTPUT_DIR/parallel_${size}x${size}_window${WINDOW_SIZE}_np2.txt"
    if [ -f "$RESULT_FILE" ]; then
        EXEC_TIME=$(grep "Execution time" "$RESULT_FILE" | awk -F': ' '{print $2}' | awk '{print $1}')
        THROUGHPUT=$(grep "Throughput" "$RESULT_FILE" | awk -F': ' '{print $2}' | awk '{print $1}')
        echo "Parallel,${size},${size},2,${EXEC_TIME},${THROUGHPUT}" >> "$DATA_FILE"
    fi
done

# Check CPU count and run 4-process benchmarks if available
NUM_CPUS=$(nproc 2>/dev/null || echo "2")
if [ "$NUM_CPUS" -ge 4 ]; then
    echo ""
    echo "Starting parallel benchmarks with 4 processes..."
    for size in "${TEST_SIZES[@]}"; do
        echo "Testing parallel (4 procs): ${size}x${size}..."
        mpirun -np 4 ./bin/median_parallel "$size" "$size" "$WINDOW_SIZE" 2>/dev/null
        
        RESULT_FILE="$OUTPUT_DIR/parallel_${size}x${size}_window${WINDOW_SIZE}_np4.txt"
        if [ -f "$RESULT_FILE" ]; then
            EXEC_TIME=$(grep "Execution time" "$RESULT_FILE" | awk -F': ' '{print $2}' | awk '{print $1}')
            THROUGHPUT=$(grep "Throughput" "$RESULT_FILE" | awk -F': ' '{print $2}' | awk '{print $1}')
            echo "Parallel,${size},${size},4,${EXEC_TIME},${THROUGHPUT}" >> "$DATA_FILE"
        fi
    done
else
    echo ""
    echo "Note: System has $NUM_CPUS CPU(s). Skipping 4-process benchmarks."
fi

echo ""
echo "Benchmarking complete!"
echo "Results saved to: $DATA_FILE"
echo ""
echo "Contents of benchmark results:"
cat "$DATA_FILE"
