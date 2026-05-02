#ifndef MEDIAN_FILTER_H
#define MEDIAN_FILTER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <sys/time.h>

typedef struct {
    int width;
    int height;
    unsigned char *data;
} Image;
Image* create_image(int width, int height);
void free_image(Image *img);
void fill_random_image(Image *img);
void apply_median_filter_sequential(Image *input, Image *output, int window_size);
unsigned char get_median(unsigned char *values, int count);
void save_ppm(const char *filename, Image *img);
void load_ppm(const char *filename, Image *img);

#endif
