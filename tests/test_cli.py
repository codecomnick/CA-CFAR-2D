import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_cli(cfar_executable: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(cfar_executable), *arguments],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_cli_requires_input_file(cfar_executable):
    result = run_cli(cfar_executable)

    assert result.returncode == 1
    assert "Uso" in result.stdout


def test_cli_rejects_missing_file(cfar_executable):
    result = run_cli(cfar_executable, "data/does-not-exist.txt")

    assert result.returncode == 1
    assert "Erro" in result.stdout


def test_cli_rejects_truncated_matrix(cfar_executable, tmp_path):
    matrix_path = tmp_path / "truncated.txt"
    matrix_path.write_text(" ".join(["1"] * 899), encoding="utf-8")

    result = run_cli(cfar_executable, str(matrix_path))

    assert result.returncode == 1
    assert "Erro" in result.stdout


def test_cli_rejects_non_numeric_token(cfar_executable, tmp_path):
    values = ["1"] * 900
    values[450] = "invalid"
    matrix_path = tmp_path / "invalid-token.txt"
    matrix_path.write_text(" ".join(values), encoding="utf-8")

    result = run_cli(cfar_executable, str(matrix_path))

    assert result.returncode == 1
    assert "Erro" in result.stdout


def test_cli_prints_detection_map_for_valid_input(cfar_executable):
    result = run_cli(cfar_executable, "data/radar_01.txt")

    assert result.returncode == 0
    assert "MAPA DE DETECCAO CA-CFAR 2D" in result.stdout
