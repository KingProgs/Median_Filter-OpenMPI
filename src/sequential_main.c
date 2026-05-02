#define _POSIX_C_SOURCE 200809L
#include "median_filter.h"
#include <time.h>

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Usage: %s <width> <height> <window_size>\n", argv[0]);
        fprintf(stderr, "Example: %s 512 512 5\n", argv[0]);
        return 1;
    }

    int width = atoi(argv[1]);
    int height = atoi(argv[2]);
    int window_size = atoi(argv[3]);

    if (width <= 0 || height <= 0 || window_size <= 0 || window_size % 2 == 0) {
        fprintf(stderr, "Invalid parameters. Window size must be odd and positive.\n");
        return 1;
    }

    printf("Sequential Median Filter\n");
    printf("Image: %d x %d pixels\n", width, height);
    printf("Window size: %d x %d\n", window_size, window_size);
    printf("Creating image...\n");

    Image *input = create_image(width, height);
    Image *output = create_image(width, height);

    fill_random_image(input);

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    apply_median_filter_sequential(input, output, window_size);

    clock_gettime(CLOCK_MONOTONIC, &end);

    double elapsed = (end.tv_sec - start.tv_sec) +
                     (end.tv_nsec - start.tv_nsec) / 1000000000.0;

    printf("Elapsed time: %.6f seconds\n", elapsed);
    printf("Pixels processed: %d\n", width * height);
    printf("Pixels per second: %.2f M/s\n", (width * height) / (elapsed * 1000000.0));

    char output_file[256];
    snprintf(output_file, sizeof(output_file), "./results/sequential_%dx%d_window%d.ppm",
             width, height, window_size);
    save_ppm(output_file, output);
    printf("Output saved to: %s\n", output_file);

    char timing_file[256];
    snprintf(timing_file, sizeof(timing_file), "./results/sequential_%dx%d_window%d.txt",
             width, height, window_size);
    FILE *fp = fopen(timing_file, "w");
    if (fp != NULL) {
        fprintf(fp, "Sequential Median Filter Results\n");
        fprintf(fp, "Image dimensions: %d x %d\n", width, height);
        fprintf(fp, "Window size: %d\n", window_size);
        fprintf(fp, "Execution time (seconds): %.6f\n", elapsed);
        fprintf(fp, "Pixels processed: %d\n", width * height);
        fprintf(fp, "Throughput (M pixels/s): %.2f\n", (width * height) / (elapsed * 1000000.0));
        fclose(fp);
    }

    free_image(input);
    free_image(output);

    return 0;
}
