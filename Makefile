# Makefile for Median Filter with OpenMPI

CC = gcc
MPICC = mpicc
CFLAGS = -Wall -Wextra -O2 -std=c99 -D_POSIX_C_SOURCE=200809L
LDFLAGS = -lm -lrt

SRC_DIR = src
BIN_DIR = bin
RESULTS_DIR = results

# Source files
COMMON_SRC = $(SRC_DIR)/median_filter.c
SEQ_SRC = $(SRC_DIR)/sequential_main.c
PAR_SRC = $(SRC_DIR)/parallel_main.c

# Object files
SEQ_OBJ = $(BIN_DIR)/median_filter_seq.o $(BIN_DIR)/sequential_main.o
PAR_OBJ = $(BIN_DIR)/median_filter_par.o $(BIN_DIR)/parallel_main.o

# Executable files
SEQ_BIN = $(BIN_DIR)/median_sequential
PAR_BIN = $(BIN_DIR)/median_parallel

# Default target
all: $(SEQ_BIN) $(PAR_BIN)

# Create directories
$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(RESULTS_DIR):
	mkdir -p $(RESULTS_DIR)

# Sequential implementation
$(BIN_DIR)/median_filter_seq.o: $(COMMON_SRC) | $(BIN_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BIN_DIR)/sequential_main.o: $(SEQ_SRC) | $(BIN_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(SEQ_BIN): $(SEQ_OBJ)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)
	@echo "Built sequential version: $@"

# Parallel implementation (OpenMPI)
$(BIN_DIR)/median_filter_par.o: $(COMMON_SRC) | $(BIN_DIR)
	$(MPICC) $(CFLAGS) -c $< -o $@

$(BIN_DIR)/parallel_main.o: $(PAR_SRC) | $(BIN_DIR)
	$(MPICC) $(CFLAGS) -c $< -o $@

$(PAR_BIN): $(PAR_OBJ)
	$(MPICC) $(CFLAGS) $^ -o $@ $(LDFLAGS)
	@echo "Built parallel version: $@"

# Build and run sequential tests
test-seq: $(SEQ_BIN) $(RESULTS_DIR)
	@echo "Testing sequential version..."
	./$(SEQ_BIN) 256 256 5
	./$(SEQ_BIN) 512 512 5
	./$(SEQ_BIN) 1024 1024 5

# Build and run parallel tests
test-par: $(PAR_BIN) $(RESULTS_DIR)
	@echo "Testing parallel version with 2 processes..."
	mpirun -np 2 ./$(PAR_BIN) 256 256 5
	mpirun -np 2 ./$(PAR_BIN) 512 512 5
	mpirun -np 2 ./$(PAR_BIN) 1024 1024 5

# Run all benchmarks
benchmark: all $(RESULTS_DIR)
	@echo "Running full benchmark suite..."
	chmod +x benchmark.sh
	./benchmark.sh
	@echo "Generating plots..."
	python3 generate_plots.py

# Clean build artifacts
clean:
	rm -f $(BIN_DIR)/*.o $(SEQ_BIN) $(PAR_BIN)
	@echo "Cleaned build artifacts"

# Clean all including results
distclean: clean
	rm -f $(RESULTS_DIR)/*
	@echo "Cleaned all results"

# Help message
help:
	@echo "Median Filter with OpenMPI - Makefile targets:"
	@echo "  make              - Build both sequential and parallel versions"
	@echo "  make test-seq     - Test sequential version"
	@echo "  make test-par     - Test parallel version"
	@echo "  make benchmark    - Run full benchmark suite"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make distclean    - Remove everything including results"
	@echo "  make help         - Show this help message"

.PHONY: all test-seq test-par benchmark clean distclean help
