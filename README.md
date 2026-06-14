# Simulador de Sistema Operacional

Trabalho pratico de Sistemas Operacionais: gerenciador e escalonador de processos.

O projeto simula um sistema com:

- 4 CPUs;
- 4 discos para operacoes de I/O;
- 32 GiB de memoria principal compartilhada;
- processos de tempo real e processos de usuario;
- escalonamento FCFS para tempo real;
- escalonamento por feedback com 3 filas para usuarios;
- quantum de 2 unidades de tempo;
- gerenciamento de memoria por blocos.

## Como executar

A execucao principal do projeto e pela interface grafica:

```powershell
python interface.py
```

Na interface e possivel executar a simulacao automaticamente ou avancar ciclo por ciclo.

Tambem existe execucao pelo terminal:

```powershell
python main.py entrada.txt
```

## Entrada

O arquivo de entrada padrao e `entrada.txt`.

Cada linha representa um processo no formato:

```text
id,cpu1,io,cpu2,memoria
```

Exemplo:

```text
7,4,2,4,800
12,10,4,8,1200
5,15,0,0,512
```

Campos:

- `id`: identificador do processo;
- `cpu1`: duracao da primeira fase de CPU;
- `io`: duracao da fase de entrada/saida;
- `cpu2`: duracao da segunda fase de CPU;
- `memoria`: memoria necessaria em MiB.

## Organizacao

```text
.
|-- interface.py
|-- main.py
|-- le_dados.py
|-- entrada.txt
`-- modelos/
    |-- processo.py
    |-- gerenciador.py
    |-- recursos.py
    `-- escalonador.py
```

## Arquivos principais

- `interface.py`: interface grafica da simulacao.
- `main.py`: execucao da simulacao pelo terminal.
- `le_dados.py`: leitura dos processos do arquivo de entrada.
- `modelos/processo.py`: classe que representa um processo.
- `modelos/gerenciador.py`: gerenciamento de memoria.
- `modelos/recursos.py`: gerenciamento dos discos de I/O.
- `modelos/escalonador.py`: filas de prontos, CPUs e politicas de escalonamento.

## Observacoes

Processos de tempo real usam apenas CPU e memoria, com limite de 512 MiB.

Processos de usuario podem passar por CPU, I/O e CPU novamente. Quando entram em I/O, utilizam um dos 4 discos disponiveis.
