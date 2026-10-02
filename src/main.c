#include <stdio.h>
#include <stdlib.h>
#include "cfar.h"

int load_matrix(
    const char *filename,
    double matrix[NUM_DOPPLER][NUM_RANGE]
) {
    FILE *file = fopen(filename, "r");

    if (file == NULL) {
        printf("Erro: nao foi possivel abrir o arquivo '%s'.\n",
               filename);
        return 0;
    }

    for (int r = 0; r < NUM_DOPPLER; r++) {
        for (int c = 0; c < NUM_RANGE; c++) {

            if (fscanf(file, "%lf", &matrix[r][c]) != 1) {
                printf(
                    "Erro: quantidade ou formato invalido de dados no arquivo.\n"
                );

                fclose(file);
                return 0;
            }
        }
    }

    fclose(file);

    return 1;
}

int main(int argc, char *argv[]) {

    // Verifica se o usuário informou o arquivo
    if (argc < 2) {
        printf("Uso: %s <arquivo_de_entrada>\n", argv[0]);
        return 1;
    }

    double data_matrix[NUM_DOPPLER][NUM_RANGE];
    int detections[NUM_DOPPLER][NUM_RANGE];

    // Carrega a matriz
    if (!load_matrix(argv[1], data_matrix)) {
        return 1;
    }

    // Executa o algoritmo CA-CFAR
    double alpha = 6.0;

    cfar_2d(
        data_matrix,
        detections,
        alpha
    );

    // Exibe o resultado
    printf("\n=== MAPA DE DETECCAO CA-CFAR 2D ===\n");
    printf("('.' = sem deteccao, 'X' = deteccao)\n\n");

    for (int r = 0; r < NUM_DOPPLER; r++) {

        for (int c = 0; c < NUM_RANGE; c++) {

            if (detections[r][c] == 1) {
                printf("X ");
            } else {
                printf(". ");
            }
        }

        printf("\n");
    }

    return 0;
}