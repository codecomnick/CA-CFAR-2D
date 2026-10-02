#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define NUM_DOPPLER 30
#define NUM_RANGE   30
// Parâmetros do CFAR
#define T_DOPPLER   3
#define T_RANGE     3
#define G_DOPPLER   1
#define G_RANGE     1

int main() {
    double data_matrix[NUM_DOPPLER][NUM_RANGE];
    int detections[NUM_DOPPLER][NUM_RANGE] = {0};

    double alpha = 6.0;

    // 1. Simulação dos dados de Radar (Ruído de fundo + Alvos)
    srand(42);

    for (int r = 0; r < NUM_DOPPLER; r++) {
        for (int c = 0; c < NUM_RANGE; c++) {
            data_matrix[r][c] = ((double)rand() / RAND_MAX) * 2.0;
        }
    }
// mudar entrada física 
 
    data_matrix[8][10]  = 10.0;
    data_matrix[15][22] = 50.0;
    data_matrix[20][5]  = 42.0;
    data_matrix[12][15] = 3.0;

    int total_window_cells =
        (2 * T_DOPPLER + 2 * G_DOPPLER + 1) *
        (2 * T_RANGE + 2 * G_RANGE + 1);

    int guard_cut_cells =
        (2 * G_DOPPLER + 1) *
        (2 * G_RANGE + 1);

    int num_train_cells =
        total_window_cells - guard_cut_cells;

    // 3. Processamento 2D CA-CFAR
    for (int r = (T_DOPPLER + G_DOPPLER);
         r < NUM_DOPPLER - (T_DOPPLER + G_DOPPLER);
         r++) {

        for (int c = (T_RANGE + G_RANGE);
             c < NUM_RANGE - (T_RANGE + G_RANGE);
             c++) {

            double sum_total = 0.0;
            double sum_guard_cut = 0.0;

            // Varredura da janela completa
            for (int wr = r - (T_DOPPLER + G_DOPPLER);
                 wr <= r + (T_DOPPLER + G_DOPPLER);
                 wr++) {

                for (int wc = c - (T_RANGE + G_RANGE);
                     wc <= c + (T_RANGE + G_RANGE);
                     wc++) {

                    sum_total += data_matrix[wr][wc];
                }
            }

            // Varredura da região Guarda + CUT
            for (int gr = r - G_DOPPLER;
                 gr <= r + G_DOPPLER;
                 gr++) {

                for (int gc = c - G_RANGE;
                     gc <= c + G_RANGE;
                     gc++) {

                    sum_guard_cut += data_matrix[gr][gc];
                }
            }

            double sum_train =
                sum_total - sum_guard_cut;

            double noise_level =
                sum_train / num_train_cells;

            double threshold =
                alpha * noise_level;

            double cut =
                data_matrix[r][c];

            if (cut > threshold) {
                detections[r][c] = 1;
            }
        }
    }

    // 4. Exibição do mapa
    printf("\n=== MAPA DE DETECCAO CFAR 2D ===\n");
    printf("('.' = RUIDO, 'X' = ALVO DETECTADO)\n\n");

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

    // 5. Procedimentos de teste

    int testes_executados = 3;
    int testes_aprovados = 0;

    printf("\n");
    printf("========================================\n");
    printf("       PROCEDIMENTOS DE TESTE\n");
    printf("========================================\n");

    // TESTE 1 - Alvo forte
    printf("\nTESTE 1 - ALVO FORTE\n");
    printf("Posicao: [15][22]\n");
    printf("Potencia: %.2f\n", data_matrix[15][22]);
    printf("Esperado: ALVO DETECTADO\n");

    if (detections[15][22] == 1) {
        printf("Obtido:   ALVO DETECTADO\n");
        printf("Status: [PASSOU]\n");
        testes_aprovados++;
    } else {
        printf("Obtido:   NAO DETECTADO\n");
        printf("Status: [FALHOU]\n");
    }

    // TESTE 2 - Ruído de fundo
    printf("\nTESTE 2 - RUIDO DE FUNDO\n");
    printf("Posicao: [10][10]\n");
    printf("Potencia: %.2f\n", data_matrix[10][10]);
    printf("Esperado: NAO DETECTADO\n");

    if (detections[10][10] == 0) {
        printf("Obtido:   NAO DETECTADO\n");
        printf("Status: [PASSOU]\n");
        testes_aprovados++;
    } else {
        printf("Obtido:   ALVO DETECTADO\n");
        printf("Status: [FALHOU]\n");
    }

    // TESTE 3 - Sinal fraco
    printf("\nTESTE 3 - SINAL FRACO\n");
    printf("Posicao: [12][15]\n");
    printf("Potencia: %.2f\n", data_matrix[12][15]);
    printf("Esperado: NAO DETECTADO\n");

    if (detections[12][15] == 0) {
        printf("Obtido:   NAO DETECTADO\n");
        printf("Status: [PASSOU]\n");
        testes_aprovados++;
    } else {
        printf("Obtido:   ALVO DETECTADO\n");
        printf("Status: [FALHOU]\n");
    }

    // Resumo dos testes
    printf("\n");
    printf("========================================\n");
    printf("          RESUMO DOS TESTES\n");
    printf("========================================\n");

    printf("Testes executados: %d\n", testes_executados);
    printf("Testes aprovados:  %d\n", testes_aprovados);
    printf("Testes falhos:     %d\n",
           testes_executados - testes_aprovados);

    if (testes_aprovados == testes_executados) {
        printf("\nRESULTADO: TODOS OS TESTES PASSARAM\n");
    } else {
        printf("\nRESULTADO: EXISTEM TESTES COM FALHA\n");
    }

    printf("========================================\n");

    return 0;
}