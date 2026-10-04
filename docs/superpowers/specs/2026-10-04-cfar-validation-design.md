# Especificacao de validacao do CA-CFAR 2D

## Objetivo

Criar uma estrategia de testes gratuita, automatizada e reproduzivel para
demonstrar que a implementacao C do CA-CFAR 2D:

1. calcula a decisao de deteccao conforme a definicao matematica adotada;
2. coincide com implementacoes independentes na regiao em que a janela esta
   completa;
3. preserva a probabilidade de falso alarme prevista pelo modelo classico em
   ruido homogeneo;
4. mantem o comportamento esperado nos cenarios fornecidos pelo projeto; e
5. nao apresenta erros de memoria ou comportamento indefinido nos testes.

A validacao nao alterara o algoritmo de producao, os parametros atuais ou o
formato dos dados. Em particular, `alpha = 6.0` continuara sendo o valor usado
por `src/main.c`.

## Escopo

### Incluido

- testes unitarios deterministas do nucleo `cfar_2d`;
- comparacao celula a celula com dois oraculos independentes;
- regressao automatizada dos cinco cenarios existentes;
- medicao estatistica da probabilidade de falso alarme;
- avaliacao empirica da probabilidade de deteccao em funcao do SNR;
- testes da interface de linha de comando e leitura de arquivos;
- compilacao com avisos estritos, AddressSanitizer e UndefinedBehaviorSanitizer;
- execucao local por um comando e execucao em CI;
- documentacao dos procedimentos, resultados e limitacoes.

### Fora do escopo

- otimizar o algoritmo;
- mudar o tratamento das bordas;
- trocar `alpha = 6.0` por um valor derivado de um `Pfa` desejado;
- implementar GO-CFAR, SO-CFAR ou OS-CFAR;
- validar desempenho em tempo real ou em hardware embarcado;
- usar MATLAB, software pago ou servicos obrigatorios externos.

## Definicao do algoritmo sob teste

Os parametros atuais sao:

- matriz: 30 x 30;
- celulas de treinamento por lado: 3 em Doppler e 3 em range;
- celulas de guarda por lado: 1 em Doppler e 1 em range;
- janela completa: 9 x 9;
- regiao central excluida: 3 x 3;
- celulas de treinamento: 72;
- fator de limiar: `alpha = 6.0`;
- decisao: detectar somente quando `CUT > alpha * media_treinamento`.

A margem da janela e 4. Portanto, somente linhas e colunas de indice 4 a 25,
inclusive, sao CUTs validas. A implementacao C deixa todas as demais celulas
com deteccao zero. Comparacoes com bibliotecas externas devem considerar apenas
essa regiao interior de 22 x 22, porque bibliotecas podem adotar preenchimento
de borda diferente.

## Oraculos de referencia

### 1. Casos analiticos

Casos construidos com valores exatos verificarao propriedades basicas sem
depender de outra implementacao. O caso principal usa 72 celulas de treinamento
com valor 1, o que produz nivel de ruido 1 e limiar 6:

- CUT igual a 6: nenhuma deteccao, pois a comparacao e estrita;
- CUT imediatamente maior que 6: deteccao;
- valores arbitrarios na regiao de guarda: nenhum efeito no limiar;
- alvo fora da regiao interior: nenhuma deteccao.

Tambem serao verificados matriz nula, matriz constante, multiplos alvos e
invariancia da decisao quando toda a matriz e multiplicada por uma constante
positiva.

### 2. Oraculo NumPy transparente

`tests/reference_cfar.py` implementara diretamente a definicao matematica com
lacos explicitos. Ele nao reutilizara codigo C, convolucao pronta ou funcao CFAR
de terceiros. Para cada CUT valida, o oraculo retornara:

- soma e media das 72 celulas de treinamento;
- limiar adaptativo;
- decisao booleana.

O objetivo desse oraculo e tornar a revisao do calculo simples e impedir que um
detalhe de indexacao fique oculto por uma primitiva de convolucao.

### 3. NRL Tracker Component Library

A comparacao externa usara `nrl-tracker==1.19.0`, distribuido pelo PyPI e
dedicado ao dominio publico/CC0. A funcao de referencia sera `cfar_2d` com:

- `guard_cells=(1, 1)`;
- `ref_cells=(3, 3)`;
- `method="ca"`;
- `alpha=6.0`.

A biblioteca fornece deteccoes, limiares e estimativas de ruido. Seus limiares
e estimativas de ruido serao comparados ao oraculo NumPy na regiao interior com
tolerancia absoluta e relativa de `1e-12`. As deteccoes da implementacao C
deverao ser identicas as dos dois oraculos nessa regiao.

Se a API publicada da versao fixada divergir da documentacao durante a primeira
instalacao reproduzivel, a implementacao sera interrompida e a especificacao
sera revisada; nao sera feita adaptacao silenciosa para obter um resultado
favoravel.

O RadarSimPy sera citado apenas como referencia adicional. Ele nao sera uma
dependencia nem criterio de aprovacao, pois sua distribuicao atual combina
codigo GPL-3.0 com binarios e mecanismo de licenca/free tier.

## Arquitetura dos testes

### Testes C

`tests/test_cfar.c` chamara `cfar_2d` diretamente e cobrira os casos analiticos.
O executavel retornara codigo diferente de zero e informara o caso que falhou.
Nenhum framework C externo sera necessario.

### Ponte Python-C

`tests/conftest.py` compilara `src/cfar.c` como biblioteca compartilhada em um
diretorio temporario do pytest e a carregara com `ctypes`. A biblioteca nao sera
gravada no repositorio. A ponte convertera matrizes NumPy 30 x 30 contiguas de
`float64` para a assinatura C e devolverá uma matriz 30 x 30 de inteiros.

No Linux sera usado `cc -shared -fPIC`; no macOS, `cc -dynamiclib -fPIC`.

### Suites Python

- `tests/test_reference.py`: casos deterministas e aleatorios comparados ao
  oraculo NumPy e ao NRL Tracker;
- `tests/test_scenarios.py`: leitura de `data/radar_XX.txt` e
  `data/radar_XX_targets.txt`, conferindo as coordenadas esperadas;
- `tests/test_statistics.py`: Monte Carlo de `Pfa` e `Pd`;
- `tests/test_cli.py`: argumentos ausentes, arquivo inexistente, arquivo
  incompleto, token invalido e execucao valida.

## Validacao estatistica

### Modelo de ruido

O ensaio de falso alarme usara amostras independentes de potencia com
distribuicao exponencial de media 1. Esse modelo corresponde a ruido complexo
gaussiano apos detector de lei quadratica, hipotese usada na expressao classica
do CA-CFAR.

Os cinco cenarios existentes, gerados com ruido uniforme em amplitude, nao
serao usados para afirmar uma probabilidade teorica de falso alarme.

### Probabilidade teorica de falso alarme

Para `N = 72` celulas de treinamento e fator `alpha`, a previsao e:

```text
Pfa = (1 + alpha / N)^(-N)
```

Com `alpha = 6.0`, o valor esperado e aproximadamente
`0.0031414369621206085`.

O teste usara semente fixa e 5.000 matrizes 30 x 30. Para preservar a
independencia exigida pelo intervalo binomial, somente nove CUTs com janelas
9 x 9 nao sobrepostas serao contadas em cada matriz: o produto cartesiano dos
indices de linha e coluna `{4, 13, 22}`. Isso produz 45.000 ensaios Bernoulli
independentes sob o modelo de ruido i.i.d. O numero de falsos alarmes sera
dividido por 45.000. O criterio de aprovacao sera o `Pfa` teorico estar contido
no intervalo de confianca binomial de Wilson de 99% calculado a partir do
resultado observado. As demais CUTs processadas pelo algoritmo nao entrarao no
calculo estatistico porque suas janelas se sobrepoem.

### Probabilidade de deteccao

Um alvo deterministico sera somado a CUT central de matrizes com o mesmo ruido
exponencial. Serao avaliados cinco niveis de SNR: 0, 5, 10, 15 e 20 dB, com
semente fixa e pelo menos 1.000 realizacoes por nivel. Os mesmos mapas de ruido
serao reutilizados em todos os niveis de SNR; somente a potencia adicionada a
CUT mudara. Esse uso de numeros aleatorios comuns torna a verificacao de
monotonicidade deterministica para cada realizacao.

O criterio de aprovacao sera que a estimativa de `Pd` nao diminua quando o SNR
aumentar e que `Pd` em 15 dB seja no minimo 0,95. Os valores medidos serao
registrados como caracterizacao do detector, nao como garantia para outros
modelos de alvo ou clutter.

## Regressao dos cenarios existentes

Com os arquivos versionados atuais e `alpha = 6.0`, os resultados esperados
sao:

| Cenario | Alvos descritos | Deteccoes esperadas | Observacao |
| --- | ---: | ---: | --- |
| Radar 01 | 3 | 3 | todos os alvos fortes |
| Radar 02 | 3 | 3 | todos os alvos em ruido maior |
| Radar 03 | 0 | 0 | nenhum falso alarme nesta realizacao |
| Radar 04 | 1 | 0 | alvo fraco abaixo do limiar |
| Radar 05 | 5 | 5 | todos os alvos fortes |

Para os cenarios 01, 02 e 05, o conjunto de coordenadas detectadas deve ser
exatamente igual ao conjunto do arquivo `_targets.txt`. O cenario 03 nao deve
ter deteccoes. O cenario 04 deve documentar explicitamente a nao deteccao do
alvo fraco; isso caracteriza o limite do parametro atual e nao e falha do teste.

## Compilacao, automacao e reproducibilidade

Sera adicionado um `Makefile` com, no minimo:

- `make build`: compilacao normal com C11 e avisos estritos;
- `make test-c`: testes unitarios C;
- `make test-python`: testes Python;
- `make test`: suite determinista completa;
- `make test-statistical`: ensaios Monte Carlo;
- `make test-sanitize`: testes C com AddressSanitizer e
  UndefinedBehaviorSanitizer.

As dependencias de teste ficarao fixadas em `requirements-test.txt`. O ambiente
minimo sera Python 3.10, compilador C com suporte a C11 e as bibliotecas Python
pytest, NumPy, SciPy e NRL Tracker nas versoes registradas no arquivo.

`.github/workflows/test.yml` executara compilacao estrita, testes C, testes
Python, testes estatisticos e sanitizers em Ubuntu. O fluxo local continuara
sendo o metodo principal e nao dependera do GitHub para funcionar.

## Documentacao e evidencias

`docs/TESTING.md` explicara:

- pre-requisitos e criacao do ambiente;
- comandos de cada nivel de teste;
- definicao da janela e das 72 celulas de treinamento;
- diferenca entre os cenarios uniformes e o ensaio exponencial;
- configuracao exata da biblioteca de referencia;
- criterios de aprovacao;
- como interpretar `Pfa`, intervalo de confianca, `Pd` e falhas;
- resultados obtidos na versao entregue;
- limitacoes e extensoes futuras.

O README apontara para esse documento e apresentara `make test` como entrada
principal de validacao.

## Criterios de conclusao

O trabalho sera considerado concluido quando:

1. todos os testes deterministas passarem localmente;
2. as deteccoes C forem identicas aos dois oraculos em todas as CUTs validas
   dos casos de comparacao;
3. os limiares do NRL Tracker e do oraculo NumPy coincidirem dentro de `1e-12`;
4. os cinco cenarios produzirem exatamente os resultados registrados;
5. o `Pfa` teorico estiver no intervalo de Wilson de 99%;
6. o ensaio de `Pd` for monotonicamente nao decrescente e atingir pelo menos
   0,95 em 15 dB;
7. compilacao estrita e sanitizers terminarem sem erros;
8. a documentacao permitir que outra pessoa reproduza todos os resultados a
   partir de um clone limpo.

## Referencias

- RadarSimPy, `cfar_ca_2d`:
  <https://radarsimx.github.io/radarsimpy/api/process.html>
- NRL Tracker Component Library, processamento de sinais e `cfar_2d`:
  <https://nedonatelli.github.io/TCL/api/signal_processing.html>
- Licenca CC0/dominio publico do NRL Tracker:
  <https://github.com/nedonatelli/TCL/blob/main/LICENSE>
- H. Rohling, "Radar CFAR Thresholding in Clutter and Multiple Target
  Situations", IEEE Transactions on Aerospace and Electronic Systems, 1983.
