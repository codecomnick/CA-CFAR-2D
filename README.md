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
2D CA CFAR/
│
├── data/
│   ├── radar_01.txt
│   ├── radar_01_targets.txt
│   ├── radar_02.txt
│   ├── radar_02_targets.txt
│   ├── radar_03.txt
│   ├── radar_03_targets.txt
│   ├── radar_04.txt
│   ├── radar_04_targets.txt
│   ├── radar_05.txt
│   └── radar_05_targets.txt
│
├── src/
│   ├── cfar.c
│   ├── cfar.h
│   └── main.c
│
├── tools/
│   └── generate_data.py
│
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

Os arquivos `radar_XX_targets.txt` armazenam as posições e potências dos alvos conhecidos e serão utilizados posteriormente para validação automatizada.

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

Esse cenário será utilizado posteriormente para avaliar falsos alarmes.

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

## 🧪 Testes e validacao

Crie um ambiente Python isolado e instale as dependencias gratuitas fixadas:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-test.txt
```

Execute a suite deterministica, os ensaios estatisticos e os sanitizers:

```bash
make test
make test-statistical
make test-sanitize
```

Os procedimentos, oraculos de referencia, criterios de aprovacao e resultados
medidos estao documentados em [docs/TESTING.md](docs/TESTING.md).

Caso o NumPy ainda não esteja instalado:

```bash
python -m pip install numpy
```

---

## 🚧 Próximos passos

O projeto será posteriormente expandido para incluir:

* Testes automatizados externos;
* Comparação entre detecções esperadas e obtidas;
* Cálculo de taxa de detecção;
* Avaliação de falsos alarmes;
* Diferentes valores de `alpha`;
* Mais cenários de teste;
* Possível adaptação para execução em hardware embarcado.

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
