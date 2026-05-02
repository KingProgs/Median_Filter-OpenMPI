#include "median_filter.h"

Image* create_image(int width, int height) {
    Image *img = (Image *)malloc(sizeof(Image));
    img->width = width;
    img->height = height;
    img->data = (unsigned char *)malloc(width * height * sizeof(unsigned char));
    memset(img->data, 0, width * height * sizeof(unsigned char));
    return img;
}

void free_image(Image *img) {
    if (img != NULL) {
        if (img->data != NULL) {
            free(img->data);
        }
        free(img);
    }
}

void fill_random_image(Image *img) {
    srand(time(NULL));
    for (int i = 0; i < img->width * img->height; i++) {
        img->data[i] = rand() % 256;
    }
}

static int compare_unsigned_char(const void *a, const void *b) {
    return (*(unsigned char *)a) - (*(unsigned char *)b);
}

unsigned char get_median(unsigned char *values, int count) {
    qsort(values, count, sizeof(unsigned char), compare_unsigned_char);
    if (count % 2 == 0) {
        return (values[count / 2 - 1] + values[count / 2]) / 2;
    } else {
        return values[count / 2];
    }
}

void apply_median_filter_sequential(Image *input, Image *output, int window_size) {
    int half_window = window_size / 2;
    int window_area = window_size * window_size;
    unsigned char *window_values = (unsigned char *)malloc(window_area * sizeof(unsigned char));

    for (int y = 0; y < input->height; y++) {
        for (int x = 0; x < input->width; x++) {
            int count = 0;

            for (int wy = -half_window; wy <= half_window; wy++) {
                for (int wx = -half_window; wx <= half_window; wx++) {
                    int ny = y + wy;
                    int nx = x + wx;

                    if (ny >= 0 && ny < input->height && nx >= 0 && nx < input->width) {
                        window_values[count++] = input->data[ny * input->width + nx];
                    }
                }
            }

            output->data[y * output->width + x] = get_median(window_values, count);
        }
    }

    free(window_values);
}

void save_ppm(const char *filename, Image *img) {
    FILE *fp = fopen(filename, "wb");
    if (fp == NULL) {
        fprintf(stderr, "Error opening file %s for writing\n", filename);
        return;
    }

    fprintf(fp, "P5\n");
    fprintf(fp, "%d %d\n", img->width, img->height);
    fprintf(fp, "255\n");
    fwrite(img->data, sizeof(unsigned char), img->width * img->height, fp);
    fclose(fp);
}

void load_ppm(const char *filename, Image *img) {
    FILE *fp = fopen(filename, "rb");
    if (fp == NULL) {
        fprintf(stderr, "Error opening file %s for reading\n", filename);
        return;
    }

    char magic[3];
    int width, height, maxval;
    fscanf(fp, "%s\n%d %d\n%d\n", magic, &width, &height, &maxval);

    if (img->width != width || img->height != height) {
        fprintf(stderr, "Image dimensions mismatch\n");
        fclose(fp);
        return;
    }

    fread(img->data, sizeof(unsigned char), width * height, fp);
    fclose(fp);
}
