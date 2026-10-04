#include <math.h>
#include <stdio.h>

#include "../src/cfar.h"

#define ALPHA 6.0
#define CUT_ROW 15
#define CUT_COL 15

static void fill_matrix(
    double matrix[NUM_DOPPLER][NUM_RANGE],
    double value
) {
    for (int row = 0; row < NUM_DOPPLER; row++) {
        for (int col = 0; col < NUM_RANGE; col++) {
            matrix[row][col] = value;
        }
    }
}

static int count_detections(
    int detections[NUM_DOPPLER][NUM_RANGE]
) {
    int count = 0;

    for (int row = 0; row < NUM_DOPPLER; row++) {
        for (int col = 0; col < NUM_RANGE; col++) {
            count += detections[row][col];
        }
    }

    return count;
}

static int test_zero_matrix(void) {
    double data[NUM_DOPPLER][NUM_RANGE];
    int detections[NUM_DOPPLER][NUM_RANGE];

    fill_matrix(data, 0.0);
    cfar_2d(data, detections, ALPHA);

    return count_detections(detections) == 0;
}

static int test_constant_matrix(void) {
    double data[NUM_DOPPLER][NUM_RANGE];
    int detections[NUM_DOPPLER][NUM_RANGE];

    fill_matrix(data, 1.0);
    cfar_2d(data, detections, ALPHA);

    return count_detections(detections) == 0;
}

static int test_threshold_comparison_is_strict(void) {
    double data[NUM_DOPPLER][NUM_RANGE];
    int detections[NUM_DOPPLER][NUM_RANGE];

    fill_matrix(data, 1.0);
    data[CUT_ROW][CUT_COL] = 6.0;
    cfar_2d(data, detections, ALPHA);
    if (detections[CUT_ROW][CUT_COL] != 0) {
        return 0;
    }

    data[CUT_ROW][CUT_COL] = nextafter(6.0, INFINITY);
    cfar_2d(data, detections, ALPHA);

    return detections[CUT_ROW][CUT_COL] == 1;
}

static int test_guard_cells_are_excluded(void) {
    double data[NUM_DOPPLER][NUM_RANGE];
    int detections[NUM_DOPPLER][NUM_RANGE];

    fill_matrix(data, 1.0);
    data[CUT_ROW][CUT_COL] = 7.0;

    for (int row = CUT_ROW - 1; row <= CUT_ROW + 1; row++) {
        for (int col = CUT_COL - 1; col <= CUT_COL + 1; col++) {
            if (row != CUT_ROW || col != CUT_COL) {
                data[row][col] = 1e9;
            }
        }
    }

    cfar_2d(data, detections, ALPHA);

    return detections[CUT_ROW][CUT_COL] == 1;
}

static int test_border_is_not_processed(void) {
    double data[NUM_DOPPLER][NUM_RANGE];
    int detections[NUM_DOPPLER][NUM_RANGE];

    fill_matrix(data, 1.0);
    data[3][3] = 1e9;
    cfar_2d(data, detections, ALPHA);

    return detections[3][3] == 0;
}

static int test_scale_invariance(void) {
    double data[NUM_DOPPLER][NUM_RANGE];
    double scaled[NUM_DOPPLER][NUM_RANGE];
    int detections[NUM_DOPPLER][NUM_RANGE];
    int scaled_detections[NUM_DOPPLER][NUM_RANGE];

    for (int row = 0; row < NUM_DOPPLER; row++) {
        for (int col = 0; col < NUM_RANGE; col++) {
            data[row][col] = 1.0 + ((row * NUM_RANGE + col) % 17) / 10.0;
        }
    }
    data[8][10] = 45.0;
    data[15][22] = 50.0;

    for (int row = 0; row < NUM_DOPPLER; row++) {
        for (int col = 0; col < NUM_RANGE; col++) {
            scaled[row][col] = data[row][col] * 3.5;
        }
    }

    cfar_2d(data, detections, ALPHA);
    cfar_2d(scaled, scaled_detections, ALPHA);

    for (int row = 0; row < NUM_DOPPLER; row++) {
        for (int col = 0; col < NUM_RANGE; col++) {
            if (detections[row][col] != scaled_detections[row][col]) {
                return 0;
            }
        }
    }

    return 1;
}

static int test_multiple_targets(void) {
    double data[NUM_DOPPLER][NUM_RANGE];
    int detections[NUM_DOPPLER][NUM_RANGE];

    fill_matrix(data, 1.0);
    data[5][5] = 10.0;
    data[15][20] = 10.0;
    data[25][25] = 10.0;

    cfar_2d(data, detections, ALPHA);

    return count_detections(detections) == 3 &&
           detections[5][5] == 1 &&
           detections[15][20] == 1 &&
           detections[25][25] == 1;
}

int main(void) {
    struct test_case {
        const char *name;
        int (*run)(void);
    } tests[] = {
        {"zero_matrix", test_zero_matrix},
        {"constant_matrix", test_constant_matrix},
        {"threshold_comparison_is_strict", test_threshold_comparison_is_strict},
        {"guard_cells_are_excluded", test_guard_cells_are_excluded},
        {"border_is_not_processed", test_border_is_not_processed},
        {"scale_invariance", test_scale_invariance},
        {"multiple_targets", test_multiple_targets},
    };
    const int test_count = (int)(sizeof(tests) / sizeof(tests[0]));

    for (int index = 0; index < test_count; index++) {
        if (!tests[index].run()) {
            fprintf(stderr, "FAIL: %s\n", tests[index].name);
            return 1;
        }
    }

    printf("%d C tests passed\n", test_count);
    return 0;
}
