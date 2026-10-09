# CA-CFAR 2D

Implementação de um algoritmo **CA-CFAR (Cell Averaging Constant False Alarm Rate) em duas dimensões**, desenvolvido em linguagem C para processamento de uma matriz Radar Range-Doppler.

O projeto foi desenvolvido no contexto da disciplina de **Sistemas Embarcados**, com foco em organização modular, processamento de dados externos e possibilidade de futura adaptação para sistemas embarcados.

---

## 📌 Sobre o projeto

O CA-CFAR é um algoritmo utilizado para detecção de alvos em dados de radar.

A ideia principal é estimar o nível de ruído ao redor de uma célula de teste e, a partir dessa estimativa, calcular um limiar de detecção adaptativo.

O algoritmo utilizado neste projeto é o **CA-CFAR 2D**, no qual a vizinhança da célula sob teste é analisada considerando as dimensões:

* Range
* Doppler

---

## ⚙️ Funcionamento

Para cada **CUT (Cell Under Test)**, o algoritmo utiliza:

* Células de treinamento (*Training Cells*)
* Células de guarda (*Guard Cells*)
* Célula sob teste (*CUT*)
* Fator `alpha`

Com os parâmetros atuais:

```text
Training Doppler = 3
Training Range   = 3

Guard Doppler = 1
Guard Range   = 1
```

A janela total possui:

```text
9 × 9 = 81 células
```

As células de guarda juntamente com a CUT ocupam:

```text
3 × 3 = 9 células
```

Portanto, são utilizadas:

```text
81 - 9 = 72 células de treinamento
```

O nível de ruído é calculado por:

```text
noise_level = soma_das_celulas_de_treinamento / número_de_células
```

O limiar é:

```text
threshold = alpha × noise_level
```

Atualmente:

```text
alpha = 6.0
```

A detecção ocorre quando:

```text
CUT > threshold
```

---

## 📁 Estrutura do projeto

```text
CA-CFAR-2D/
│
├── .github/
│   └── workflows/
│       └── test.yml
│
├── data/
│   ├── radar_01.txt
│   ├── radar_01_targets.txt
│   └── ...
│
├── docs/
│   └── TESTING.md
│
├── src/
│   ├── cfar.c
│   ├── cfar.h
│   └── main.c
│
├── tests/
│   ├── test_cfar.c
│   ├── test_cli.py
│   ├── test_reference.py
│   ├── test_scenarios.py
│   ├── test_statistics.py
│   └── reference_cfar.py
│
├── tools/
│   └── generate_data.py
│
├── Makefile
├── pytest.ini
├── requirements-test.txt
└── README.md
```

---

## 🧩 Organização dos arquivos

### `src/cfar.c`

Contém a implementação do algoritmo CA-CFAR 2D.

O algoritmo recebe uma matriz de entrada e produz uma matriz de detecções.

A implementação não possui geração de dados, testes ou alvos fixos.

---

### `src/cfar.h`

Contém as definições e parâmetros utilizados pelo algoritmo, além da declaração da função principal:

```c
cfar_2d()
```

---

### `src/main.c`

Responsável pela execução do programa.

Suas principais funções são:

1. Receber o arquivo de entrada;
2. Carregar a matriz;
3. Executar o algoritmo CA-CFAR;
4. Exibir o mapa de detecção.

Exemplo:

```bash
./cfar.exe data/radar_01.txt
```

---

### `data/`

Contém os dados de entrada utilizados pelo algoritmo.

Os arquivos `radar_XX.txt` possuem matrizes de:

```text
30 × 30
```

Os arquivos `radar_XX_targets.txt` armazenam as posições e potências dos alvos conhecidos e são usados pela validação automatizada.

---

### `tools/generate_data.py`

Script Python responsável pela geração dos cenários de entrada.

O script utiliza a biblioteca NumPy para gerar matrizes de ruído e inserir alvos em posições específicas.

Foram criados diferentes cenários para avaliar o comportamento do algoritmo em diferentes condições.

---

## 🧪 Cenários disponíveis

### Radar 01

Ruído entre `0` e `2`, contendo três alvos fortes.

```text
[8][10]  = 45
[15][22] = 50
[20][5]  = 42
```

### Radar 02

Ruído entre `0` e `10`, contendo os mesmos três alvos.

Esse cenário permite observar o comportamento do algoritmo diante de um nível de ruído maior.

### Radar 03

Ruído entre `0` e `2`, sem alvos.

Esse cenário verifica a ausência de detecções nos dados versionados. A taxa
teórica de falsos alarmes é avaliada separadamente com ruído exponencial e
amostras independentes, como descrito em `docs/TESTING.md`.

### Radar 04

Ruído entre `0` e `2`, contendo um alvo de baixa potência:

```text
[15][15] = 3
```

### Radar 05

Ruído entre `0` e `2`, contendo cinco alvos:

```text
[5][5]   = 35
[7][20]  = 40
[12][15] = 50
[18][8]  = 45
[22][25] = 55
```

---

## ▶️ Como executar

### 1. Compilar

No diretório raiz do projeto:

```bash
gcc src/main.c src/cfar.c -o cfar.exe
```

### 2. Executar

```bash
./cfar.exe data/radar_01.txt
```

Também é possível executar os outros cenários:

```bash
./cfar.exe data/radar_02.txt
./cfar.exe data/radar_03.txt
./cfar.exe data/radar_04.txt
./cfar.exe data/radar_05.txt
```

---

## 🐍 Gerar novos dados

Para gerar novamente os cenários:

```bash
python tools/generate_data.py
```

---

## 🧪 Testes e validação

A validação foi construída apenas com ferramentas gratuitas e reproduzíveis.
As versões de `pytest`, NumPy, SciPy e NRL Tracker estão fixadas em
[`requirements-test.txt`](requirements-test.txt), e os testes aleatórios usam a
semente `20261004`.

### Preparação do ambiente

Pré-requisitos:

* compilador C com suporte a C11;
* Make;
* Python 3.10 ou superior.

Crie o ambiente virtual:

```bash
python3 -m venv .venv
```

Ative-o no Bash ou Zsh:

```bash
source .venv/bin/activate
```

No Fish, use o script específico do shell:

```fish
source .venv/bin/activate.fish
```

Instale e verifique as dependências:

```bash
python -m pip install -r requirements-test.txt
python -m pip check
```

### Como executar

```bash
# 7 testes C e 17 testes rápidos em Python
make test

# 2 ensaios estatísticos de Pfa e Pd
make test-statistical

# 7 testes C instrumentados com ASan e UBSan
make test-sanitize
```

Para executar toda a sequência a partir de uma compilação limpa:

```bash
make clean
make test
make test-statistical
make test-sanitize
```

### Escopo das suítes

Os números abaixo pertencem a grupos diferentes e não devem ser interpretados
como se todos fossem testes dos cinco arquivos `radar_XX.txt`.

| Grupo | Quantidade | O que verifica |
| --- | ---: | --- |
| Testes unitários em C | 7 | matriz nula e constante, limiar estrito, células de guarda, bordas, invariância de escala e múltiplos alvos |
| Testes rápidos em Python | 17 | oráculos de referência, 20 mapas aleatórios, cinco cenários versionados, CLI e independência das janelas estatísticas |
| Testes estatísticos em Python | 2 | probabilidade de falso alarme (`Pfa`) e probabilidade de detecção (`Pd`) |

Os 17 testes rápidos em Python são compostos por:

* 6 testes do algoritmo e dos oráculos de referência;
* 5 casos parametrizados, um para cada cenário versionado;
* 5 testes da interface de linha de comando;
* 1 teste que confirma que as janelas amostradas no ensaio de `Pfa` não se
  sobrepõem.

### Comparação com referências independentes

A implementação C é comparada com duas referências:

1. **Oráculo NumPy:** implementação explícita em
   [`tests/reference_cfar.py`](tests/reference_cfar.py), independente do código
   C. Ela percorre a janela `9 × 9`, exclui a região central `3 × 3`, calcula a
   média das 72 células de treinamento e aplica a mesma decisão estrita
   `CUT > threshold`.
2. **NRL Tracker 1.19.0:** biblioteca externa em domínio público/CC0, usada
   com o método CA-CFAR e os mesmos parâmetros do projeto.

A comparação usa 20 mapas de ruído exponencial gerados com semente fixa. Cada
mapa possui uma região válida de `22 × 22`, totalizando 9.680 decisões
comparadas. Na região interior:

* ruído e limiar do NumPy e do NRL Tracker devem coincidir com tolerância
  `1e-12`;
* as matrizes de detecção produzidas por C, NumPy e NRL Tracker devem ser
  idênticas;
* as quatro linhas e colunas de borda devem permanecer sem detecções.

### Cenários versionados

Os cinco cenários armazenados em `data/` funcionam como testes de regressão com
resultados conhecidos:

| Cenário | Condição | Detecções esperadas |
| --- | --- | ---: |
| Radar 01 | três alvos fortes, ruído entre 0 e 2 | 3 |
| Radar 02 | três alvos fortes, ruído entre 0 e 10 | 3 |
| Radar 03 | somente ruído, sem alvos | 0 |
| Radar 04 | um alvo de potência 3, abaixo do limiar | 0 |
| Radar 05 | cinco alvos fortes em posições distintas | 5 |

Cada linha da tabela corresponde a um dos cinco casos parametrizados em
[`tests/test_scenarios.py`](tests/test_scenarios.py). Portanto, esses cenários
representam apenas 5 dos 17 testes rápidos em Python.

### Ensaios estatísticos

O teste de falso alarme gera 5.000 mapas de ruído exponencial e avalia nove
CUTs com janelas que não se sobrepõem, totalizando 45.000 ensaios. Para 72
células de treinamento e `alpha = 6.0`, a previsão matemática é:

```text
Pfa = (1 + alpha / 72)^(-72) = 0.003141436962
```

O resultado observado foi `0.002977777778`, equivalente a 134 falsos alarmes.
O intervalo de Wilson de 99% foi
`[0.002385431469, 0.003716666526]`, contendo a previsão teórica.

O teste de detecção utiliza 1.000 realizações para cada nível de SNR e verifica
se a `Pd` não diminui quando o alvo fica mais forte:

| SNR | 0 dB | 5 dB | 10 dB | 15 dB | 20 dB |
| ---: | ---: | ---: | ---: | ---: | ---: |
| `Pd` | 0,6% | 6,3% | 100% | 100% | 100% |

Além da monotonicidade, o critério exige `Pd >= 95%` em 15 dB.

### Segurança da implementação C

`make test-sanitize` recompila a suíte C com:

* **AddressSanitizer (ASan):** detecta acessos inválidos e erros de memória;
* **UndefinedBehaviorSanitizer (UBSan):** detecta operações com comportamento
  indefinido em C.

Na execução de referência, os sete testes terminaram sem diagnósticos dos
sanitizers. A compilação também usa `-Wall -Wextra -Wpedantic -Werror` para
tratar avisos como erros.

### Integração contínua

O workflow [`.github/workflows/test.yml`](.github/workflows/test.yml) repete
automaticamente a instalação das dependências, os testes determinísticos, os
ensaios estatísticos e os sanitizers em cada `push` e `pull_request`.

Os procedimentos completos, critérios de aprovação, limitações e valores de
referência estão documentados em [`docs/TESTING.md`](docs/TESTING.md).

---

## 🚧 Próximos passos

Possíveis extensões futuras:

* Avaliar diferentes valores de `alpha`;
* Adicionar modelos Swerling e clutter não homogêneo;
* Criar mais cenários de teste;
* Medir tempo e consumo de memória em hardware embarcado.

---

## 👨‍💻 Desenvolvimento

Projeto desenvolvido em **C**, com geração de dados utilizando **Python + NumPy**.

O projeto utiliza uma arquitetura modular para separar:

```text
Entrada de dados
       ↓
Processamento CA-CFAR
       ↓
Saída / Detecção
       ↓
Testes e validação
```
