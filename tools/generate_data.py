import numpy as np
from pathlib import Path


# ============================================================
# CONFIGURAÇÕES
# ============================================================

ROWS = 30
COLS = 30

DATA_DIR = Path("data")

SEED = 42


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def generate_noise(min_value, max_value):
    """
    Gera uma matriz de ruído uniforme.
    """

    return np.random.uniform(
        min_value,
        max_value,
        (ROWS, COLS)
    )


def add_targets(matrix, targets):
    """
    Insere os alvos na matriz.

    targets:
        lista de tuplas (linha, coluna, potência)
    """

    for row, col, power in targets:
        matrix[row, col] = power


def save_matrix(filename, matrix):
    """
    Salva a matriz no formato utilizado pelo programa em C.
    """

    np.savetxt(
        filename,
        matrix,
        fmt="%.2f"
    )


def save_targets(filename, targets):
    """
    Salva as posições e potências dos alvos.
    """

    with open(filename, "w") as file:

        for row, col, power in targets:

            file.write(
                f"{row} {col} {power:.2f}\n"
            )


def create_scenario(number, noise_min, noise_max, targets):
    """
    Cria um cenário completo:
    
    radar_XX.txt
    radar_XX_targets.txt
    """

    matrix = generate_noise(
        noise_min,
        noise_max
    )

    add_targets(
        matrix,
        targets
    )

    radar_file = DATA_DIR / f"radar_{number:02d}.txt"

    targets_file = DATA_DIR / f"radar_{number:02d}_targets.txt"

    save_matrix(
        radar_file,
        matrix
    )

    save_targets(
        targets_file,
        targets
    )

    print(f"[OK] radar_{number:02d}.txt")


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    # Cria a pasta data caso ela não exista
    DATA_DIR.mkdir(
        exist_ok=True
    )

    # Garante que os mesmos dados sejam gerados
    # sempre que utilizarmos a mesma seed.
    np.random.seed(SEED)


    # ========================================================
    # CENÁRIO 1
    # Ruído baixo + 3 alvos fortes
    # ========================================================

    create_scenario(
        number=1,

        noise_min=0.0,
        noise_max=2.0,

        targets=[
            (8, 10, 45.0),
            (15, 22, 50.0),
            (20, 5, 42.0)
        ]
    )


    # ========================================================
    # CENÁRIO 2
    # Ruído mais elevado + 3 alvos
    # ========================================================

    create_scenario(
        number=2,

        noise_min=0.0,
        noise_max=10.0,

        targets=[
            (8, 10, 45.0),
            (15, 22, 50.0),
            (20, 5, 42.0)
        ]
    )


    # ========================================================
    # CENÁRIO 3
    # Somente ruído
    # Não existem alvos
    # ========================================================

    create_scenario(
        number=3,

        noise_min=0.0,
        noise_max=2.0,

        targets=[]
    )


    # ========================================================
    # CENÁRIO 4
    # Alvo fraco
    # ========================================================

    create_scenario(
        number=4,

        noise_min=0.0,
        noise_max=2.0,

        targets=[
            (15, 15, 3.0)
        ]
    )


    # ========================================================
    # CENÁRIO 5
    # Vários alvos em posições diferentes
    # ========================================================

    create_scenario(
        number=5,

        noise_min=0.0,
        noise_max=2.0,

        targets=[
            (5, 5, 35.0),
            (7, 20, 40.0),
            (12, 15, 50.0),
            (18, 8, 45.0),
            (22, 25, 55.0)
        ]
    )


    print()
    print("======================================")
    print("GERACAO DE DADOS CONCLUIDA")
    print("======================================")
    print(f"Matriz: {ROWS} x {COLS}")
    print(f"Cenarios gerados: 5")
    print(f"Seed: {SEED}")
    print("======================================")


if __name__ == "__main__":
    main()