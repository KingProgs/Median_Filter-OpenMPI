#define _POSIX_C_SOURCE 200809L
#include <mpi.h>
#include "median_filter.h"

void apply_median_filter_parallel(Image *input, Image *output, int window_size, int rank, int size) {
    int half_window = window_size / 2;
    int window_area = window_size * window_size;
    unsigned char *window_values = (unsigned char *)malloc(window_area * sizeof(unsigned char));

    int rows_per_process = input->height / size;
    int extra_rows = input->height % size;
    
    int start_row = rank * rows_per_process + (rank < extra_rows ? rank : extra_rows);
    int num_rows = rows_per_process + (rank < extra_rows ? 1 : 0);

    int buffer_height = num_rows + 2 * half_window;
    unsigned char *buffer = (unsigned char *)malloc(buffer_height * input->width * sizeof(unsigned char));

    MPI_Request request[4];
    int request_count = 0;
    MPI_Status status[4];

    if (rank > 0) {
        MPI_Irecv(buffer, half_window * input->width, MPI_UNSIGNED_CHAR, rank - 1, 0, MPI_COMM_WORLD, &request[request_count++]);
    }

    if (rank < size - 1) {
        int recv_offset = (num_rows + half_window) * input->width;
        MPI_Irecv(buffer + recv_offset, half_window * input->width, MPI_UNSIGNED_CHAR, rank + 1, 0, MPI_COMM_WORLD, &request[request_count++]);
    }

    if (rank > 0) {
        MPI_Isend(input->data, half_window * input->width, MPI_UNSIGNED_CHAR, rank - 1, 0, MPI_COMM_WORLD, &request[request_count++]);
    }

    if (rank < size - 1) {
        int send_offset = (num_rows - half_window) * input->width;
        MPI_Isend(input->data + send_offset * sizeof(unsigned char), half_window * input->width, MPI_UNSIGNED_CHAR, rank + 1, 0, MPI_COMM_WORLD, &request[request_count++]);
    }

    memcpy(buffer + half_window * input->width, input->data, num_rows * input->width * sizeof(unsigned char));

    if (request_count > 0) {
        MPI_Waitall(request_count, request, status);
    }

    for (int y = 0; y < num_rows; y++) {
        for (int x = 0; x < input->width; x++) {
            int count = 0;

            for (int wy = -half_window; wy <= half_window; wy++) {
                for (int wx = -half_window; wx <= half_window; wx++) {
                    int by = y + half_window + wy;
                    int nx = x + wx;

                    if (by >= 0 && by < buffer_height && nx >= 0 && nx < input->width) {
                        window_values[count++] = buffer[by * input->width + nx];
                    }
                }
            }

            output->data[(start_row + y) * output->width + x] = get_median(window_values, count);
        }
    }

    free(window_values);
    free(buffer);
}

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc < 4) {
        if (rank == 0) {
            fprintf(stderr, "Usage: %s <width> <height> <window_size>\n", argv[0]);
            fprintf(stderr, "Example: mpirun -np 4 %s 512 512 5\n", argv[0]);
        }
        MPI_Finalize();
        return 1;
    }

    int width = atoi(argv[1]);
    int height = atoi(argv[2]);
    int window_size = atoi(argv[3]);

    if (width <= 0 || height <= 0 || window_size <= 0 || window_size % 2 == 0) {
        if (rank == 0) {
            fprintf(stderr, "Invalid parameters. Window size must be odd and positive.\n");
        }
        MPI_Finalize();
        return 1;
    }

    if (rank == 0) {
        printf("Parallel Median Filter (OpenMPI)\n");
        printf("Number of processes: %d\n", size);
        printf("Image: %d x %d pixels\n", width, height);
        printf("Window size: %d x %d\n", window_size, window_size);
    }

    Image *input = create_image(width, height);
    Image *output = create_image(width, height);

    if (rank == 0) {
        fill_random_image(input);
    }

    MPI_Bcast(input->data, width * height, MPI_UNSIGNED_CHAR, 0, MPI_COMM_WORLD);

    MPI_Barrier(MPI_COMM_WORLD);

    double start_time = MPI_Wtime();

    apply_median_filter_parallel(input, output, window_size, rank, size);

    MPI_Barrier(MPI_COMM_WORLD);
    double end_time = MPI_Wtime();

    int rows_per_process = height / size;
    int extra_rows = height % size;

    for (int p = 0; p < size; p++) {
        int start_row = p * rows_per_process + (p < extra_rows ? p : extra_rows);
        int num_rows = rows_per_process + (p < extra_rows ? 1 : 0);

        if (rank == p && p != 0) {
            MPI_Send(output->data + start_row * width, num_rows * width, MPI_UNSIGNED_CHAR, 0, p, MPI_COMM_WORLD);
        } else if (rank == 0 && p != 0) {
            MPI_Recv(output->data + start_row * width, num_rows * width, MPI_UNSIGNED_CHAR, p, p, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        }
    }

    if (rank == 0) {
        double elapsed = end_time - start_time;

        printf("Elapsed time: %.6f seconds\n", elapsed);
        printf("Pixels processed: %d\n", width * height);
        printf("Pixels per second: %.2f M/s\n", (width * height) / (elapsed * 1000000.0));

        char output_file[256];
        snprintf(output_file, sizeof(output_file), "./results/parallel_%dx%d_window%d_np%d.ppm",
                 width, height, window_size, size);
        save_ppm(output_file, output);
        printf("Output saved to: %s\n", output_file);

        char timing_file[256];
        snprintf(timing_file, sizeof(timing_file), "./results/parallel_%dx%d_window%d_np%d.txt",
                 width, height, window_size, size);
        FILE *fp = fopen(timing_file, "w");
        if (fp != NULL) {
            fprintf(fp, "Parallel Median Filter Results (OpenMPI)\n");
            fprintf(fp, "Number of processes: %d\n", size);
            fprintf(fp, "Image dimensions: %d x %d\n", width, height);
            fprintf(fp, "Window size: %d\n", window_size);
            fprintf(fp, "Execution time (seconds): %.6f\n", elapsed);
            fprintf(fp, "Pixels processed: %d\n", width * height);
            fprintf(fp, "Throughput (M pixels/s): %.2f\n", (width * height) / (elapsed * 1000000.0));
            fclose(fp);
        }
    }

    free_image(input);
    free_image(output);

    MPI_Finalize();
    return 0;
}