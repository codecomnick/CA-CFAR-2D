#ifndef CFAR_H
#define CFAR_H

#define NUM_DOPPLER 30
#define NUM_RANGE 30

#define T_DOPPLER 3
#define T_RANGE 3

#define G_DOPPLER 1
#define G_RANGE 1

void cfar_2d(
    double data_matrix[NUM_DOPPLER][NUM_RANGE],
    int detections[NUM_DOPPLER][NUM_RANGE],
    double alpha
);

#endif
