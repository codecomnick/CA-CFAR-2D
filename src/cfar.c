#include "cfar.h"

void cfar_2d(
double data_matrix[NUM_DOPPLER][NUM_RANGE],
int detections[NUM_DOPPLER][NUM_RANGE],
double alpha
) {
    // Inicializa a matriz de detecções com zero
    for (int r = 0; r < NUM_DOPPLER; r++) {
        for (int c = 0; c < NUM_RANGE; c++) {
            detections[r][c] = 0;
        }
    }

    // Calcula o tamanho da janela completa
    int total_window_cells =
        (2 * T_DOPPLER + 2 * G_DOPPLER + 1) *
        (2 * T_RANGE + 2 * G_RANGE + 1);

    // Calcula a quantidade de células da região de guarda + CUT
    int guard_cut_cells =
        (2 * G_DOPPLER + 1) *
        (2 * G_RANGE + 1);

    // Quantidade de células utilizadas para estimar o ruído
    int num_train_cells =
        total_window_cells - guard_cut_cells;

    // Percorre somente as posições onde a janela cabe completamente
    for (
        int r = T_DOPPLER + G_DOPPLER;
        r < NUM_DOPPLER - (T_DOPPLER + G_DOPPLER);
        r++
    ) {
        for (
            int c = T_RANGE + G_RANGE;
            c < NUM_RANGE - (T_RANGE + G_RANGE);
            c++
        ) {

            double sum_total = 0.0;
            double sum_guard_cut = 0.0;

            // Soma da janela completa
            for (
                int wr = r - (T_DOPPLER + G_DOPPLER);
                wr <= r + (T_DOPPLER + G_DOPPLER);
                wr++
            ) {
                for (
                    int wc = c - (T_RANGE + G_RANGE);
                    wc <= c + (T_RANGE + G_RANGE);
                    wc++
                ) {
                    sum_total += data_matrix[wr][wc];
                }
            }

            // Soma da região de guarda + CUT
            for (
                int gr = r - G_DOPPLER;
                gr <= r + G_DOPPLER;
                gr++
            ) {
                for (
                    int gc = c - G_RANGE;
                    gc <= c + G_RANGE;
                    gc++
                ) {
                    sum_guard_cut += data_matrix[gr][gc];
                }
            }

            // Remove a região central
            double sum_train =
                sum_total - sum_guard_cut;

            // Estima o nível médio do ruído
            double noise_level =
                sum_train / num_train_cells;

            // Calcula o limiar adaptativo
            double threshold =
                alpha * noise_level;

            // Célula sob teste
            double cut =
                data_matrix[r][c];

            // Decisão
            if (cut > threshold) {
                detections[r][c] = 1;
            }
        }
    }
}