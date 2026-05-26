# Planejamento Scrum - Simulador de Sistema Operacional

## Visao Geral

O objetivo do projeto e implementar, em Python, um simulador de sistema operacional com escalonamento de processos, quatro CPUs, quatro discos e 32 GiB de memoria principal compartilhada.

O simulador deve permitir acompanhar a execucao dos processos ao longo do tempo, mostrando criacao, mudancas de estado, uso das CPUs, filas de prontos, processos bloqueados por I/O, uso de memoria e uso dos discos.

Unidade de tempo sugerida:

```text
1 u.t. = 1 ciclo da simulacao
```

A simulacao pode avancar por ciclos discretos. Cada ciclo representa uma unidade de tempo usada para reduzir o tempo restante de CPU ou I/O dos processos.

---

## Sprint 1 - Estrutura Inicial do Simulador

### 1. Definir o formato do arquivo de entrada

Criar um arquivo de texto contendo a lista de processos que serao executados pelo simulador.

Formato sugerido:

```text
# id, chegada, prioridade, cpu1, io, cpu2, memoriaMB, discos
1,0,0,6,0,0,256,0
2,1,1,8,4,6,1200,1
3,2,1,15,0,0,512,2
4,3,0,4,0,0,128,0
```

Campos:

```text
id          = identificador do processo
chegada     = tempo em que o processo entra no sistema
prioridade  = 0 para tempo real, 1 para usuario
cpu1        = duracao da primeira fase de CPU
io          = duracao da fase de I/O
cpu2        = duracao da segunda fase de CPU
memoriaMB   = memoria necessaria em MiB
discos      = quantidade de discos necessarios
```

O grupo deve criar uma entrada significativa, com processos variados, incluindo:

- processos de tempo real;
- processos de usuario;
- processos CPU-bound, sem fase de I/O;
- processos com fase de I/O;
- processos que usem discos;
- processos que provoquem espera por memoria ou recursos.

### 2. Criar a classe `Processo`

Implementar uma classe para representar cada processo da simulacao.

Atributos sugeridos:

```python
id
tempo_chegada
prioridade
cpu1_total
io_total
cpu2_total
memoria_mb
discos_necessarios
estado
fase_atual
cpu_restante
io_restante
quantum_usado
```

Estados possiveis:

```text
NOVO
PRONTO
EXECUTANDO
BLOQUEADO
FINALIZADO
ESPERANDO_MEMORIA
ESPERANDO_RECURSO
```

A classe deve permitir:

- identificar em qual fase o processo esta;
- saber quanto tempo ainda resta da fase atual;
- saber se o processo terminou;
- atualizar o estado do processo.

### 3. Criar mensagens de criacao e mudanca de estado

O simulador deve mostrar mensagens sempre que um processo for criado ou mudar de estado.

Exemplos:

```text
[t=0] Criando Processo #1
[t=0] Processo #1: NOVO -> PRONTO
[t=1] Processo #1: PRONTO -> EXECUTANDO na CPU 0
[t=6] Processo #1: EXECUTANDO -> FINALIZADO
```

Essas mensagens ajudam a acompanhar a vida de cada processo dentro do sistema.

---

## Sprint 2 - Memoria e Recursos

### 1. Implementar o gerenciador de memoria

O sistema possui:

```text
32 GiB = 32768 MiB de memoria principal
```

A memoria nao deve ser apenas descontada de um total. O simulador deve representar a memoria como blocos ou particoes.

Modelo sugerido: particoes variaveis com First Fit.

Exemplo de representacao interna:

```python
[
    {"inicio": 0, "tamanho": 512, "livre": False, "pid": 1},
    {"inicio": 512, "tamanho": 1200, "livre": False, "pid": 2},
    {"inicio": 1712, "tamanho": 31056, "livre": True, "pid": None}
]
```

O gerenciador de memoria deve:

- iniciar com um unico bloco livre de 32768 MiB;
- procurar espaco usando First Fit;
- alocar memoria para um processo;
- dividir blocos quando necessario;
- liberar memoria quando o processo terminar;
- unir blocos livres vizinhos apos a liberacao.

### 2. Validar processos de tempo real

Processos de tempo real possuem prioridade `0` e podem usar no maximo:

```text
512 MiB de memoria
```

O simulador deve verificar essa regra no momento da leitura ou submissao do processo.

Se um processo de tempo real solicitar mais de 512 MiB, o sistema deve mostrar uma mensagem de erro e rejeitar esse processo.

### 3. Implementar o gerenciador de recursos

O sistema possui:

```text
4 CPUs
4 discos
32768 MiB de RAM
```

As CPUs serao controladas pelo escalonador. Os discos devem ser controlados por um gerenciador de recursos.

O gerenciador de recursos deve:

- controlar quantos discos estao disponiveis;
- alocar discos para processos de usuario;
- manter os discos reservados durante toda a execucao do processo;
- liberar os discos quando o processo finalizar;
- colocar processos em espera quando nao houver discos suficientes.

Processos de tempo real nao usam discos, apenas CPU e memoria.

---

## Sprint 3 - Escalonamento de Processos

### 1. Implementar a fila de tempo real com FCFS

Processos de tempo real:

- possuem prioridade `0`;
- sao os processos de maior prioridade do sistema;
- usam a politica FCFS;
- nao sofrem interrupcao;
- executam ate a conclusao;
- precisam apenas de CPU e memoria.

O escalonador deve sempre escolher processos de tempo real antes dos processos de usuario.

Se houver CPU livre e processo de tempo real pronto, ele deve ser despachado imediatamente.

### 2. Implementar feedback com tres filas para processos de usuario

Processos de usuario possuem prioridade `1` e devem ser escalonados por uma politica de feedback com tres filas.

Filas sugeridas:

```text
Fila 1 - maior prioridade entre usuarios
Fila 2 - prioridade intermediaria
Fila 3 - menor prioridade entre usuarios
```

Quantum:

```text
2 u.t.
```

Regras sugeridas:

- processo de usuario novo entra na Fila 1;
- se usar todo o quantum e ainda precisar de CPU, desce uma fila;
- se estiver na Fila 1, vai para a Fila 2;
- se estiver na Fila 2, vai para a Fila 3;
- se estiver na Fila 3, permanece na Fila 3;
- se bloquear por I/O antes de terminar o quantum, sai da CPU;
- apos terminar I/O, pode voltar para a Fila 1.

### 3. Implementar o controle de I/O

Um processo pode ter as seguintes fases:

```text
CPU fase 1
I/O
CPU fase 2
```

Ou pode ter apenas CPU fase 1, representando um processo CPU-bound.

O simulador deve:

- mover o processo para bloqueado quando terminar CPU fase 1 e ainda tiver I/O;
- reduzir o tempo restante de I/O a cada ciclo;
- mover o processo de volta para a fila de prontos quando o I/O terminar;
- executar CPU fase 2 depois do I/O;
- finalizar o processo quando nao houver mais fases.

### 4. Implementar as quatro CPUs

O sistema possui quatro CPUs compartilhando a mesma memoria principal.

O simulador deve representar as CPUs como uma lista:

```python
cpus = [None, None, None, None]
```

Cada CPU pode estar:

- livre;
- executando um processo de tempo real;
- executando um processo de usuario.

A cada ciclo, o simulador deve:

- verificar quais CPUs estao livres;
- buscar processos prontos para executar;
- colocar ate quatro processos em execucao ao mesmo tempo;
- reduzir o tempo restante de CPU dos processos em execucao.

---

## Sprint 4 - Despachante e Loop da Simulacao

### 1. Criar o despachante

O despachante sera responsavel por controlar a entrada dos processos no sistema.

Responsabilidades do despachante:

- verificar quais processos chegam no tempo atual;
- criar o descritor do processo;
- tentar alocar memoria;
- tentar alocar recursos, como discos;
- colocar o processo na fila correta;
- manter processos esperando memoria em uma fila separada;
- manter processos esperando recursos em outra fila separada;
- chamar o escalonador para preencher CPUs livres.

Fila de processos esperando:

```text
Fila de espera por memoria
Fila de espera por recurso
Fila de prontos de tempo real
Fila 1 de usuarios
Fila 2 de usuarios
Fila 3 de usuarios
Fila de bloqueados por I/O
```

### 2. Criar o loop principal da simulacao

O loop principal controla a passagem do tempo.

Fluxo sugerido para cada ciclo:

```text
1. Criar processos que chegaram no tempo atual
2. Tentar atender processos esperando memoria
3. Tentar atender processos esperando recursos
4. Atualizar processos bloqueados por I/O
5. Escalonar processos para CPUs livres
6. Executar um ciclo nas CPUs ocupadas
7. Verificar finalizacoes, bloqueios e preempcoes
8. Mostrar o estado atual do sistema
9. Avancar o tempo
```

A simulacao termina quando:

- todos os processos foram criados;
- nao ha processos em filas de pronto;
- nao ha processos bloqueados;
- nao ha processos esperando memoria ou recurso;
- todas as CPUs estao livres.

### 3. Garantir a prioridade dos processos de tempo real

O despachante e o escalonador devem garantir que processos de tempo real tenham prioridade sobre os processos de usuario.

Regras importantes:

- processo de tempo real pronto deve ser escolhido antes de qualquer processo de usuario;
- processo de tempo real nao sofre preempcao;
- processo de usuario pode ser interrompido pelo fim do quantum;
- processos de tempo real seguem FCFS.

---

## Sprint 5 - Interface, Relatorio e Entrada Final

### 1. Criar a interface textual da simulacao

A interface pode ser feita no terminal, imprimindo o estado do sistema a cada ciclo.

Exemplo de saida:

```text
==================================================
Tempo: 12

CPUs:
CPU 0: Processo #4 - Tempo real
CPU 1: Processo #8 - Usuario Fila 2
CPU 2: Livre
CPU 3: Processo #9 - Usuario Fila 1

Filas:
Tempo real: [10, 11]
Usuario F1: [3, 7]
Usuario F2: [2]
Usuario F3: [5, 6]
Bloqueados I/O: [12]
Esperando memoria: [14]
Esperando recurso: [15]

Memoria:
Usada: 4300 MiB / 32768 MiB
Livre: 28468 MiB

Discos:
Usados: 3 / 4
==================================================
```

A interface deve facilitar o acompanhamento de:

- tempo atual;
- processos em cada CPU;
- filas de prontos;
- processos bloqueados por I/O;
- processos esperando memoria;
- processos esperando recurso;
- uso de memoria;
- uso dos discos.

### 2. Gerar relatorio final

Ao final da simulacao, o programa deve apresentar um resumo da execucao.

Informacoes sugeridas:

```text
Tempo total da simulacao
Quantidade de processos finalizados
Quantidade de processos de tempo real
Quantidade de processos de usuario
Tempo medio de espera
Tempo medio de turnaround
Uso medio das CPUs
Uso maximo de memoria
Quantidade de vezes que processos esperaram por memoria
Quantidade de vezes que processos esperaram por recurso
```

Para cada processo, tambem pode ser mostrado:

```text
ID do processo
Tempo de chegada
Tempo de inicio
Tempo de termino
Turnaround
Tempo total de espera
```

### 3. Criar uma entrada final significativa

O grupo deve montar um arquivo de entrada completo para demonstrar o simulador.

Requisitos sugeridos:

- pelo menos 20 processos;
- pelo menos 5 processos de tempo real;
- varios processos de usuario;
- processos que usam 0, 1, 2, 3 e 4 discos;
- processos com I/O;
- processos CPU-bound;
- processos que precisam esperar por memoria;
- processos que precisam esperar por disco.

Exemplo inicial:

```text
# id, chegada, prioridade, cpu1, io, cpu2, memoriaMB, discos
1,0,0,5,0,0,256,0
2,0,1,8,4,6,1200,1
3,1,1,15,0,0,512,0
4,2,0,4,0,0,128,0
5,2,1,6,3,5,4096,2
6,3,1,10,0,0,2048,1
7,4,1,12,5,6,8192,3
8,5,0,3,0,0,512,0
9,5,1,9,2,4,1024,4
10,6,1,20,0,0,16384,0
11,7,0,6,0,0,256,0
12,8,1,7,4,7,6000,2
13,9,1,5,0,0,7000,1
14,10,1,8,6,5,12000,3
15,11,0,5,0,0,300,0
16,12,1,11,0,0,4096,2
17,13,1,4,2,3,2048,1
18,14,1,16,0,0,10000,0
19,15,0,4,0,0,512,0
20,16,1,9,5,8,4096,4
```

### 4. Documentar o uso de threads no simulador

O relatorio deve explicar como o simulador poderia se beneficiar de multiplas threads.

Texto sugerido:

```text
O simulador poderia ser beneficiado por threads separando responsabilidades.
Uma thread poderia cuidar da interface, outra do avanco da simulacao, outra
da coleta de estatisticas e outra do registro de logs. Isso permitiria que a
interface continuasse responsiva enquanto a simulacao executa.

Apesar disso, os processos simulados nao precisam ser implementados como
threads reais. Como o objetivo e simular o escalonamento, cada processo pode
ser representado por um objeto Python atualizado a cada unidade de tempo.
```

---

## Organizacao Sugerida dos Arquivos

```text
simulador/
  main.py
  processo.py
  estados.py
  memoria.py
  recursos.py
  escalonador.py
  despachante.py
  interface.py
  entrada.txt
```

---

## Divisao Sugerida do Trabalho

```text
Aluno 1: entrada, classe Processo, estados e logs
Aluno 2: memoria e recursos
Aluno 3: escalonadores de tempo real e usuario
Aluno 4: despachante, loop da simulacao e interface
Todos: entrada final, testes manuais e relatorio
```

---

## Resultado Esperado

Ao final da Sprint 5, o grupo deve ter:

- simulador funcionando em Python;
- leitura de processos por arquivo;
- gerenciamento real de memoria por blocos;
- controle de discos;
- quatro CPUs simuladas;
- escalonamento FCFS para tempo real;
- escalonamento feedback com tres filas para usuarios;
- controle de I/O;
- interface textual para acompanhar a execucao;
- relatorio final da simulacao;
- entrada significativa para demonstracao.
