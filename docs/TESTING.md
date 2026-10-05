# Procedimentos de teste e validacao

Este documento descreve como verificar a implementacao CA-CFAR 2D de forma
gratuita e reproduzivel. A validacao combina casos analiticos, uma implementacao
independente em NumPy, uma biblioteca externa de referencia, cenarios
versionados, ensaios estatisticos e verificacao de memoria.

## Configuracao validada

O algoritmo sob teste usa:

- matriz Range-Doppler 30 x 30;
- 3 celulas de treinamento por lado em cada dimensao;
- 1 celula de guarda por lado em cada dimensao;
- janela completa 9 x 9;
- regiao de guarda mais CUT 3 x 3;
- 72 celulas de treinamento;
- `alpha = 6.0`;
- decisao estrita `CUT > alpha * media_do_ruido`.

A janela completa cabe apenas nas linhas e colunas 4 a 25. Assim, a regiao
comparavel possui 22 x 22 CUTs. As bordas permanecem zeradas na implementacao C
e nao sao comparadas com bibliotecas que possam usar outro preenchimento.

## Pre-requisitos

- compilador C com suporte a C11;
- Make;
- Python 3.10 ou superior;
- acesso ao PyPI somente durante a instalacao inicial.

Crie um ambiente isolado e instale as versoes fixadas:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-test.txt
python -m pip check
```

As dependencias diretas estao fixadas em `requirements-test.txt`, inclusive
`nrl-tracker==1.19.0`.

## Comandos

### Suite deterministica

```bash
make test
```

Executa sete testes unitarios C e os testes Python nao estatisticos. A suite
cobre:

- matriz nula e matriz constante;
- comparacao estrita no limiar;
- exclusao das celulas de guarda;
- bordas nao processadas;
- invariancia por escala positiva;
- multiplos alvos;
- igualdade entre C e o oraculo NumPy;
- igualdade com o NRL Tracker;
- cinco cenarios versionados;
- erros e execucao valida da CLI.

### Probabilidade de falso alarme e deteccao

```bash
make test-statistical
```

Os ensaios usam sementes fixas, portanto sao reproduziveis. Para mostrar os
valores medidos, execute:

```bash
python -m pytest tests/test_statistics.py -m statistical -q -s
```

### Memoria e comportamento indefinido

```bash
make test-sanitize
```

Esse alvo recompila os testes C com AddressSanitizer e
UndefinedBehaviorSanitizer.

### Sequencia completa

```bash
python -m pip check
make clean
make test
make test-statistical
make test-sanitize
```

## Oraculos de referencia

### Casos analiticos

Quando todas as 72 celulas de treinamento valem 1, a media do ruido vale 1 e o
limiar vale 6. Uma CUT igual a 6 nao deve ser detectada; a menor representacao
`double` maior que 6 deve ser detectada. Esse caso verifica a comparacao `>` sem
usar outra implementacao.

### NumPy

`tests/reference_cfar.py` percorre explicitamente cada janela 9 x 9, ignora a
regiao central 3 x 3 e calcula ruido, limiar e deteccao. O codigo nao usa
convolucao nem reutiliza a implementacao C.

### NRL Tracker Component Library

A comparacao externa usa a funcao `cfar_2d` do
[NRL Tracker Component Library](https://nedonatelli.github.io/TCL/api/signal_processing.html),
um projeto em dominio publico/CC0 baseado na biblioteca do U.S. Naval Research
Laboratory. A chamada de referencia usa:

```python
cfar_2d(
    data,
    guard_cells=(1, 1),
    ref_cells=(3, 3),
    method="ca",
    alpha=6.0,
)
```

Na regiao interior, ruido e limiar devem coincidir com o oraculo NumPy usando
`rtol=1e-12` e `atol=1e-12`. As matrizes de deteccao de C, NumPy e NRL devem ser
identicas.

O [RadarSimPy](https://radarsimx.github.io/radarsimpy/api/process.html) oferece
outro `cfar_ca_2d` e serve como referencia documental. Ele nao e dependencia ou
criterio de aprovacao por causa do modelo atual de distribuicao com binarios e
free tier.

## Validacao da probabilidade de falso alarme

O modelo classico considera potencia de ruido exponencial independente, que
corresponde a ruido complexo gaussiano apos detector de lei quadratica. Para
`N` celulas de treinamento:

```text
Pfa = (1 + alpha / N)^(-N)
```

Para `N = 72` e `alpha = 6.0`:

```text
Pfa teorico = 0.0031414369621206085
```

As deteccoes vizinhas de uma matriz compartilham celulas e nao sao ensaios
binomiais independentes. Por isso, o teste conta somente as nove CUTs formadas
pelo produto cartesiano dos indices `{4, 13, 22}`. Suas janelas 9 x 9 nao se
sobrepoem. Com 5.000 matrizes independentes, sao obtidos 45.000 ensaios.

O teste passa quando o `Pfa` teorico esta dentro do intervalo binomial de
Wilson de 99% calculado a partir do resultado observado.

## Validacao da probabilidade de deteccao

O teste adiciona um alvo deterministico a CUT `(15, 15)` sobre ruido
exponencial. Sao usadas 1.000 realizacoes nos SNRs 0, 5, 10, 15 e 20 dB. Os
mesmos mapas de ruido sao reutilizados em todos os niveis; apenas a potencia do
alvo muda. Assim, aumentar o SNR nao pode transformar uma deteccao existente em
nao deteccao por causa de uma nova amostra aleatoria.

Os criterios sao:

- `Pd` monotonicamente nao decrescente;
- `Pd >= 0.95` em 15 dB.

## Resultados de referencia

Resultados obtidos em 4 de outubro de 2026 com Python 3.14.7, NumPy 2.3.3,
NRL Tracker 1.19.0 e Apple Clang 21.0.0 em macOS arm64:

| Verificacao | Resultado |
| --- | --- |
| Testes C | 7 aprovados |
| Testes Python deterministas | 17 aprovados; 2 estatisticos desmarcados |
| Testes estatisticos | 2 aprovados |
| Sanitizers | sem diagnosticos |
| Falsos alarmes | 134 em 45.000 |
| `Pfa` observado | 0.002977777778 |
| Intervalo de Wilson 99% | [0.002385431469, 0.003716666526] |
| `Pfa` teorico | 0.003141436962 |
| `Pd` em 0, 5, 10, 15 e 20 dB | 0.006, 0.063, 1.000, 1.000, 1.000 |

O `Pfa` teorico esta contido no intervalo de 99%, e a sequencia de `Pd` atende
aos dois criterios.

## Regressao dos arquivos versionados

| Cenario | Alvos descritos | Deteccoes esperadas |
| --- | ---: | ---: |
| Radar 01 | 3 | 3, nas mesmas coordenadas |
| Radar 02 | 3 | 3, nas mesmas coordenadas |
| Radar 03 | 0 | 0 |
| Radar 04 | 1 | 0 |
| Radar 05 | 5 | 5, nas mesmas coordenadas |

O alvo de potencia 3 no Radar 04 fica abaixo do limiar atual. A nao deteccao e
uma caracterizacao conhecida de `alpha = 6.0`, nao uma falha da suite.

## Criterios de aprovacao

A versao e aceita quando:

1. compilacao C11 com `-Wall -Wextra -Wpedantic -Werror` termina sem avisos;
2. os testes C e Python deterministas passam;
3. C e os dois oraculos concordam em todas as CUTs comparadas;
4. os cinco cenarios produzem exatamente as coordenadas registradas;
5. o `Pfa` teorico pertence ao intervalo de Wilson de 99%;
6. `Pd` e monotonicamente nao decrescente e chega a 0,95 em 15 dB;
7. ASan e UBSan nao encontram erros.

## Limitacoes

- Os arquivos `radar_XX.txt` usam ruido uniforme e nao validam o `Pfa` teorico.
- Os resultados de `Pd` caracterizam um alvo deterministico em clutter
  homogeneo; nao cobrem modelos Swerling, clutter nao homogeneo ou alvos
  interferentes.
- Nao ha teste de tempo real, consumo de memoria em hardware embarcado ou
  precisao em ponto flutuante reduzido.
- O algoritmo nao processa bordas; mudar essa politica exige novos criterios e
  novos testes.
