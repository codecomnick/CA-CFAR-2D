# CA-CFAR 2D Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar uma suite gratuita e reproduzivel que valide a implementacao C por casos analiticos, dois oraculos independentes, regressao dos cenarios e ensaios estatisticos.

**Architecture:** O nucleo C permanecera inalterado e sera exercitado por um executavel de testes C e por uma biblioteca compartilhada temporaria carregada via `ctypes`. Um oraculo NumPy explicito e o `cfar_2d` do NRL Tracker serao comparados somente nas CUTs interiores; ensaios Monte Carlo separados medirao `Pfa` e `Pd` com sementes fixas.

**Tech Stack:** C11, Make, Python 3.10+, pytest, NumPy, NRL Tracker Component Library 1.19.0, GitHub Actions, AddressSanitizer e UndefinedBehaviorSanitizer.

**Spec:** `docs/superpowers/specs/2026-10-04-cfar-validation-design.md`

## Global Constraints

- Manter `src/cfar.c`, `src/cfar.h`, o tratamento de bordas e `alpha = 6.0` sem alteracoes funcionais.
- Considerar como CUTs validas somente linhas e colunas de indice 4 a 25, inclusive.
- Usar exatamente 72 celulas de treinamento e excluir a regiao central 3 x 3.
- Aplicar a decisao estrita `CUT > alpha * media_treinamento`.
- Usar somente ferramentas gratuitas; `nrl-tracker==1.19.0` e a unica biblioteca CFAR externa obrigatoria.
- Comparar limiar e ruido dos oraculos com `rtol=1e-12` e `atol=1e-12`.
- Usar ruido de potencia exponencial de media 1 nos testes estatisticos.
- Usar sementes fixas e registrar no repositorio todos os comandos e versoes necessarios.
- Nao usar os cenarios de ruido uniforme para afirmar um `Pfa` teorico.

## Review Focus

- CUT exatamente igual ao limiar deve permanecer sem deteccao; o teste pertence a Task 1.
- Guarda e CUT nao podem participar da media das 72 celulas; os testes pertencem as Tasks 1 e 2.
- Bordas devem ficar zeradas em C e devem ser excluidas das comparacoes externas; os testes pertencem as Tasks 1 a 3.
- Ensaios usados no intervalo de Wilson devem ter janelas sem sobreposicao; o teste de selecao pertence a Task 5.
- Arquivos truncados ou com token invalido devem falhar sem produzir mapa parcial; os testes pertencem a Task 4.

---

### Task 1: Build reproduzivel e testes unitarios C

**Files:**
- Create: `Makefile`
- Create: `.gitignore`
- Create: `tests/test_cfar.c`
- Test: `tests/test_cfar.c`

**Interfaces:**
- Consumes: `cfar_2d(double[30][30], int[30][30], double)` de `src/cfar.h`.
- Produces: `build/cfar`, `build/test_cfar` e os alvos Make `build`, `test-c`, `test-sanitize`, `clean`.

- [ ] **Step 1: Escrever o harness C e os casos analiticos**

Adicionar funcoes de teste com retorno booleano e mensagens contendo o nome do caso:

```c
static int test_zero_matrix(void);
static int test_constant_matrix(void);
static int test_threshold_comparison_is_strict(void);
static int test_guard_cells_are_excluded(void);
static int test_border_is_not_processed(void);
static int test_scale_invariance(void);
static int test_multiple_targets(void);
```

Em `test_threshold_comparison_is_strict`, preencher as 72 celulas de treinamento
com `1.0`, verificar ausencia de deteccao para CUT `6.0` e deteccao para
`nextafter(6.0, INFINITY)`. Em `test_guard_cells_are_excluded`, alterar somente
as oito celulas de guarda para `1e9` e confirmar que a decisao nao muda.

- [ ] **Step 2: Executar o alvo ainda inexistente e confirmar a falha**

Run: `make test-c`

Expected: FAIL com `No rule to make target 'test-c'`.

- [ ] **Step 3: Implementar o Makefile e regras de build**

Usar `-std=c11 -Wall -Wextra -Wpedantic -Werror` na compilacao normal, criar
`build/` sob demanda e ligar `tests/test_cfar.c` com `src/cfar.c` e `-lm`.
`test-sanitize` deve recompilar o teste C com
`-fsanitize=address,undefined -fno-omit-frame-pointer` e executa-lo.

Adicionar a `.gitignore`: `build/`, `.venv/`, `__pycache__/`, `.pytest_cache/`,
`*.pyc`, `*.so` e `*.dylib`.

- [ ] **Step 4: Executar testes C e sanitizers**

Run: `make test-c`

Expected: PASS e resumo `7 C tests passed`.

Run: `make test-sanitize`

Expected: PASS, sem diagnosticos de AddressSanitizer ou UndefinedBehaviorSanitizer.

- [ ] **Step 5: Commit**

```bash
git add Makefile .gitignore tests/test_cfar.c
git commit -m "test: add deterministic CA-CFAR C tests"
```

### Task 2: Ponte Python-C e oraculo NumPy transparente

**Files:**
- Create: `requirements-test.txt`
- Create: `tests/conftest.py`
- Create: `tests/cfar_test_support.py`
- Create: `tests/reference_cfar.py`
- Create: `tests/test_reference.py`
- Modify: `Makefile`
- Test: `tests/test_reference.py`

**Interfaces:**
- Consumes: `src/cfar.c`, `src/cfar.h` e compilador indicado por `CC`.
- Produces: `CfarCLibrary.detect(data: numpy.ndarray, alpha: float) -> numpy.ndarray`.
- Produces: `CfarReferenceResult(detections, threshold, noise_estimate)`.
- Produces: `ca_cfar_2d_reference(data: numpy.ndarray, alpha: float) -> CfarReferenceResult`.
- Produces: fixture pytest `c_detector: CfarCLibrary` com escopo de sessao.

- [ ] **Step 1: Fixar dependencias diretas de teste**

Registrar exatamente `pytest==8.4.2`, `numpy==2.3.3`, `scipy==1.16.2` e
`nrl-tracker==1.19.0` em `requirements-test.txt`. Validar a instalacao em Python
3.12 com:

Run: `python -m pip install -r requirements-test.txt`

Expected: exit 0 e `python -m pip check` sem conflitos.

- [ ] **Step 2: Escrever primeiro os testes do oraculo e da ponte**

Cobrir:

```python
def test_reference_rejects_wrong_shape(): ...
def test_reference_has_72_training_cells(): ...
def test_c_matches_reference_for_exact_threshold_cases(c_detector): ...
def test_c_matches_reference_for_seeded_random_maps(c_detector): ...
def test_c_and_reference_leave_border_clear(c_detector): ...
```

Usar `numpy.random.default_rng(20261004)` e exatamente 20 mapas exponenciais
30 x 30 na comparacao aleatoria. Exigir igualdade booleana exata na regiao
`[4:26, 4:26]` e borda C totalmente zerada.

- [ ] **Step 3: Executar os testes e confirmar a falha de importacao**

Run: `python -m pytest tests/test_reference.py -q`

Expected: FAIL porque `cfar_test_support` e `reference_cfar` ainda nao existem.

- [ ] **Step 4: Implementar o oraculo NumPy**

Definir `CfarReferenceResult` como `NamedTuple`. Validar matriz `float64` 30 x
30 e `alpha` finito e positivo. Percorrer explicitamente indices 4 a 25,
somando a janela 9 x 9 e subtraindo a regiao 3 x 3, sem usar convolucao.
Inicializar ruido, limiar e deteccao com zero nas bordas.

- [ ] **Step 5: Implementar a ponte ctypes e a fixture**

`build_cfar_library(output_dir: Path, compiler: str) -> CfarCLibrary` deve usar
`cc -shared -fPIC` no Linux e `cc -dynamiclib -fPIC` no macOS. Configurar
`argtypes` para ponteiros de matrizes C contiguas e `ctypes.c_double`, copiar a
entrada para `float64` C-contiguous e devolver uma copia `numpy.int32` 30 x 30.

- [ ] **Step 6: Integrar pytest ao Makefile e executar**

Adicionar `test-python` com `python -m pytest -m "not statistical" -q` e fazer
`test` depender de `test-c` e `test-python`.

Run: `make test-python`

Expected: PASS em todos os testes de `tests/test_reference.py`.

- [ ] **Step 7: Commit**

```bash
git add Makefile requirements-test.txt tests/conftest.py tests/cfar_test_support.py tests/reference_cfar.py tests/test_reference.py
git commit -m "test: compare C detector with NumPy oracle"
```

### Task 3: Comparacao com NRL Tracker Component Library

**Files:**
- Modify: `tests/test_reference.py`
- Modify: `tests/reference_cfar.py`
- Test: `tests/test_reference.py`

**Interfaces:**
- Consumes: `pytcl.mathematical_functions.signal_processing.detection.cfar_2d(image, guard_cells, ref_cells, pfa=1e-6, method="ca", alpha=None)`.
- Consumes: `CfarCLibrary.detect` e `ca_cfar_2d_reference` da Task 2.
- Produces: `nrl_ca_cfar_2d(data: numpy.ndarray, alpha: float) -> CfarReferenceResult`.
- Produces: teste de conformidade tripla entre C, NumPy e NRL Tracker.

- [ ] **Step 1: Escrever o teste de API e equivalencia NRL**

Escrever o teste contra a nova funcao `nrl_ca_cfar_2d`, ainda inexistente. Ela
devera importar `cfar_2d` pelo caminho exato acima e chama-lo com
`guard_cells=(1, 1)`, `ref_cells=(3, 3)`, `method="ca"`, `alpha=6.0`. Para os
mesmos 20 mapas aleatorios da Task 2, verificar na regiao interior:

```python
np.testing.assert_allclose(nrl.noise_estimate[inner], oracle.noise_estimate[inner], rtol=1e-12, atol=1e-12)
np.testing.assert_allclose(nrl.threshold[inner], oracle.threshold[inner], rtol=1e-12, atol=1e-12)
np.testing.assert_array_equal(nrl.detections[inner], oracle.detections[inner])
np.testing.assert_array_equal(c_result[inner].astype(bool), nrl.detections[inner])
```

- [ ] **Step 2: Executar e confirmar que o teste novo inicialmente falha**

Run: `python -m pytest tests/test_reference.py -q`

Expected: FAIL porque `nrl_ca_cfar_2d` ainda nao existe. Se, ao implementar o
adaptador, a assinatura de
`nrl-tracker==1.19.0` divergir, parar e revisar a especificacao; nao trocar de
versao silenciosamente.

- [ ] **Step 3: Completar a adaptacao de tipos sem criar outro algoritmo**

Implementar `nrl_ca_cfar_2d` em `tests/reference_cfar.py`, convertendo somente
os campos retornados pela biblioteca para `CfarReferenceResult` com arrays
NumPy. Nao normalizar, recalcular ou corrigir os valores do NRL Tracker antes
das assertivas.

- [ ] **Step 4: Executar a comparacao tripla**

Run: `python -m pytest tests/test_reference.py -q`

Expected: PASS, incluindo igualdade exata de deteccoes e tolerancia `1e-12`
para ruido e limiar.

- [ ] **Step 5: Commit**

```bash
git add tests/reference_cfar.py tests/test_reference.py
git commit -m "test: cross-check CA-CFAR with NRL Tracker"
```

### Task 4: Regressao dos cenarios e interface CLI

**Files:**
- Create: `tests/test_scenarios.py`
- Create: `tests/test_cli.py`
- Modify: `tests/conftest.py`
- Test: `tests/test_scenarios.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: fixture `c_detector` da Task 2.
- Produces: fixture `cfar_executable: pathlib.Path`, compilada em diretorio temporario.
- Produces: `load_target_coordinates(path: Path) -> set[tuple[int, int]]` no proprio modulo de cenarios.

- [ ] **Step 1: Escrever testes parametrizados dos cinco cenarios**

Fixar os conjuntos esperados explicitamente no teste:

```text
radar_01: {(8,10), (15,22), (20,5)}
radar_02: {(8,10), (15,22), (20,5)}
radar_03: {}
radar_04: {}
radar_05: {(5,5), (7,20), (12,15), (18,8), (22,25)}
```

Nos cenarios 01, 02 e 05, tambem confirmar que o conjunto lido do arquivo
`_targets.txt` coincide com o conjunto esperado. No cenario 04, confirmar que o
arquivo descreve `(15, 15)`, mas a saida permanece vazia.

- [ ] **Step 2: Escrever testes da CLI**

Cobrir ausencia de argumento, arquivo inexistente, menos de 900 numeros, token
nao numerico e arquivo valido. Exigir exit code 1 e mensagem `Uso` quando o
argumento estiver ausente; exigir exit code 1 e mensagem `Erro` nos demais
casos invalidos; no caso valido exigir exit 0 e o cabecalho do mapa.

- [ ] **Step 3: Executar e confirmar a falha pela fixture ausente**

Run: `python -m pytest tests/test_scenarios.py tests/test_cli.py -q`

Expected: FAIL porque `cfar_executable` ainda nao foi definida.

- [ ] **Step 4: Implementar a fixture de executavel temporario**

Compilar `src/main.c` e `src/cfar.c` com as mesmas flags estritas da Task 1,
gravando o executavel em `tmp_path_factory`. Nao criar binarios no repositorio.

- [ ] **Step 5: Executar a regressao completa**

Run: `python -m pytest tests/test_scenarios.py tests/test_cli.py -q`

Expected: PASS nos cinco cenarios e em todos os caminhos de erro da CLI.

- [ ] **Step 6: Commit**

```bash
git add tests/conftest.py tests/test_scenarios.py tests/test_cli.py
git commit -m "test: automate scenarios and CLI validation"
```

### Task 5: Ensaios estatisticos de Pfa e Pd

**Files:**
- Create: `pytest.ini`
- Create: `tests/statistics_support.py`
- Create: `tests/test_statistics.py`
- Modify: `Makefile`
- Test: `tests/test_statistics.py`

**Interfaces:**
- Consumes: fixture `c_detector` da Task 2.
- Produces: `wilson_interval(successes: int, trials: int, confidence: float) -> tuple[float, float]`.
- Produces: marcador pytest `statistical` e alvo Make `test-statistical`.

- [ ] **Step 1: Escrever o teste de independencia das CUTs amostradas**

Importar `wilson_interval` de `statistics_support`, que ainda nao existe.
Definir `SAMPLED_INDICES = (4, 13, 22)` e construir os nove retangulos 9 x 9.
O teste deve verificar que a intersecao entre quaisquer dois conjuntos de
coordenadas e vazia e que todas as janelas cabem na matriz.

- [ ] **Step 2: Escrever o teste de Pfa**

Com `default_rng(20261004)`, gerar 5.000 mapas exponenciais independentes,
executar C e contar deteccoes somente no produto cartesiano de
`SAMPLED_INDICES`. Calcular `expected_pfa = (1 + 6 / 72) ** -72` e exigir que
ele esteja no intervalo de Wilson de 99% dos 45.000 ensaios.

- [ ] **Step 3: Escrever o teste de Pd com numeros aleatorios comuns**

Gerar 1.000 mapas base com semente `20261004`. Para cada mapa, adicionar a CUT
`(15, 15)` uma potencia `10 ** (snr_db / 10)` para SNRs `(0, 5, 10, 15, 20)`.
Reutilizar o mesmo mapa base em todos os niveis. Exigir `Pd[i+1] >= Pd[i]` e
`Pd(15 dB) >= 0.95`.

- [ ] **Step 4: Executar antes de registrar o marcador**

Run: `python -m pytest tests/test_statistics.py --strict-markers -q`

Expected: FAIL porque `statistics_support` ainda nao existe e o marcador
`statistical` ainda nao esta registrado.

- [ ] **Step 5: Registrar marcador e alvo Make**

Implementar `wilson_interval` pela formula de Wilson usando
`statistics.NormalDist().inv_cdf` para obter o quantil. Adicionar `statistical`
a `pytest.ini`. Fazer `test-statistical` executar
`python -m pytest -m statistical -q` e marcar os dois ensaios Monte Carlo; o
teste estrutural das janelas deve permanecer na suite rapida.

- [ ] **Step 6: Executar os ensaios e registrar os valores observados**

Run: `make test-statistical`

Expected: PASS; a saida em modo verboso deve permitir registrar falsos alarmes,
`Pfa` observado, intervalo de Wilson e os cinco valores de `Pd`.

- [ ] **Step 7: Commit**

```bash
git add Makefile pytest.ini tests/statistics_support.py tests/test_statistics.py
git commit -m "test: measure false alarm and detection probabilities"
```

### Task 6: CI, procedimentos e evidencia final

**Files:**
- Create: `.github/workflows/test.yml`
- Create: `docs/TESTING.md`
- Modify: `README.md`
- Test: complete test suite

**Interfaces:**
- Consumes: todos os alvos Make e resultados das Tasks 1 a 5.
- Produces: workflow Ubuntu/Python 3.12 e procedimento local reproduzivel.

- [ ] **Step 1: Escrever o workflow CI**

Usar `actions/checkout@v7` e `actions/setup-python@v7`, Python 3.12, cache de
pip, instalacao de `requirements-test.txt`, `pip check`, `make test`,
`make test-statistical` e `make test-sanitize`.

- [ ] **Step 2: Executar localmente exatamente a sequencia do CI**

Run: `python -m pip check && make clean && make test && make test-statistical && make test-sanitize`

Expected: todos os comandos com exit 0, compilacao sem warnings e sanitizers
sem diagnosticos.

- [ ] **Step 3: Escrever `docs/TESTING.md` com resultados reais**

Documentar ambiente, instalacao, comandos, janela 9 x 9, 72 celulas, formula de
`Pfa`, razao das nove janelas nao sobrepostas, configuracao NRL, criterios de
aprovacao e limitacoes. Copiar da execucao da Step 2 os valores efetivamente
observados de `Pfa`, intervalo de Wilson e `Pd`; nao usar valores estimados ou
campos pendentes.

- [ ] **Step 4: Atualizar README**

Adicionar uma secao curta `Testes e validacao` com criacao de `.venv`,
instalacao de `requirements-test.txt`, `make test`, `make test-statistical`,
`make test-sanitize` e link relativo para `docs/TESTING.md`.

- [ ] **Step 5: Verificar links, arvore limpa de artefatos e suite final**

Run: `rg -n "TESTING.md|make test|make test-statistical|make test-sanitize" README.md docs/TESTING.md`

Expected: todos os comandos e o link documentados.

Run: `git status --short`

Expected: somente arquivos fonte/documentacao pretendidos; nenhum binario,
cache Python ou ambiente virtual rastreado.

Run: `make clean && make test && make test-statistical && make test-sanitize`

Expected: PASS integral.

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/test.yml docs/TESTING.md README.md
git commit -m "docs: publish reproducible CFAR validation procedure"
```
