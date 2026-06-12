import sys
from collections import deque
import time
from le_dados import carregar_processos
from modelos.escalonador import Escalonador
from modelos.gerenciador import GerenciadorMemoria
from modelos.recursos import GerenciadorRecursos


def mudar_estado(processo, novo_estado, tempo):
    anterior = processo.estado
    processo.alterar_estado(novo_estado)
    print(f"[t={tempo}] Processo #{processo.pid}: {anterior} -> {novo_estado}")


def criar_processo(processo, tempo, memoria, escalonador, esperando_memoria):
    print(f"[t={tempo}] Criando Processo #{processo.pid}")

    if processo.prioridade == 0 and processo.ram > 512:
        print(f"[t={tempo}] ERRO: Processo #{processo.pid} tempo real solicitou {processo.ram} MiB")
        return False

    if processo.prioridade == 0 and (processo.io > 0 or processo.cpu2 > 0):
        print(f"[t={tempo}] ERRO: Processo #{processo.pid} tempo real nao pode usar I/O")
        return False

    if not memoria.alocar(processo):
        mudar_estado(processo, "ESPERANDO_MEMORIA", tempo)
        esperando_memoria.append(processo)
        return True

    anterior = processo.estado
    escalonador.adicionar_processo(processo)
    print(f"[t={tempo}] Processo #{processo.pid}: {anterior} -> PRONTO")
    return True


def tentar_atender_fila_memoria(memoria, escalonador, esperando_memoria, tempo):
    proximos = deque()

    while esperando_memoria:
        processo = esperando_memoria.popleft()

        if memoria.alocar(processo):
            anterior = processo.estado
            escalonador.adicionar_processo(processo)
            print(f"[t={tempo}] Processo #{processo.pid}: {anterior} -> PRONTO")
        else:
            processo.tempo_espera += 1
            proximos.append(processo)

    return proximos


def processar_io_concluido(recursos, escalonador, tempo):
    finalizados_io = recursos.executar_ciclo()

    for processo in finalizados_io:
        escalonador.voltar_do_io(processo)
        print(f"[t={tempo}] Processo #{processo.pid}: BLOQUEADO -> PRONTO (retorno de I/O)")


def escalonar_processos_prontos(escalonador, tempo):
    eventos_escalonamento = escalonador.escalonar()

    for evento, processo in eventos_escalonamento:
        if evento == "preemptado":
            print(f"[t={tempo}] Processo #{processo.pid}: EXECUTANDO -> PRONTO (preemptado por tempo real)")


def imprimir_estado(tempo, escalonador, memoria, recursos, esperando_memoria):
    print("\n" + "=" * 50)
    print(f"Tempo: {tempo}\n")

    escalonador.mostrar_escalonador()

    print("=== FILAS DE ESPERA ===")
    print(f"Esperando memoria: {[processo.pid for processo in esperando_memoria]}")
    print(f"Bloqueados I/O: {recursos.ids_bloqueados()}")

    memoria.mostrar_memoria()
    recursos.mostrar_recursos()
    print("=" * 50)


def simular(arquivo_entrada):
    fila_novos = carregar_processos(arquivo_entrada)
    fila_novos = deque(sorted(fila_novos, key=lambda p: (p.tempo_chegada, p.pid)))

    memoria = GerenciadorMemoria()
    recursos = GerenciadorRecursos()
    escalonador = Escalonador()

    esperando_memoria = deque()
    tempo = 0
    finalizados = []

    while True:
        time.sleep(1)
        while fila_novos and fila_novos[0].tempo_chegada == tempo:
            processo = fila_novos.popleft()
            criar_processo(processo, tempo, memoria, escalonador, esperando_memoria)

        escalonar_processos_prontos(escalonador, tempo)

        eventos = escalonador.executar_ciclo()

        for evento, processo in eventos:
            if evento == "io":
                recursos.enviar_para_io(processo)
                print(f"[t={tempo}] Processo #{processo.pid}: EXECUTANDO -> BLOQUEADO")
            elif evento == "finalizado":
                memoria.liberar(processo.pid)
                finalizados.append(processo)
                print(f"[t={tempo}] Processo #{processo.pid}: EXECUTANDO -> FINALIZADO")
            elif evento == "quantum":
                print(f"[t={tempo}] Processo #{processo.pid}: EXECUTANDO -> PRONTO (quantum esgotado)")
            elif evento == "pronto":
                print(f"[t={tempo}] Processo #{processo.pid}: EXECUTANDO -> PRONTO")

        processar_io_concluido(recursos, escalonador, tempo)

        esperando_memoria = tentar_atender_fila_memoria(
            memoria, escalonador, esperando_memoria, tempo
        )

        escalonar_processos_prontos(escalonador, tempo)

        imprimir_estado(tempo, escalonador, memoria, recursos, esperando_memoria)

        if (
            not fila_novos
            and not esperando_memoria
            and not escalonador.tem_pendente()
            and not recursos.tem_pendente()
        ):
            break

        tempo += 1

    print(f"\nSimulacao finalizada em {tempo} ciclos")
    print(f"Processos finalizados: {len(finalizados)}")
    print(f"Processos de tempo real: {sum(1 for p in finalizados if p.prioridade == 0)}")
    print(f"Processos de usuario: {sum(1 for p in finalizados if p.prioridade == 1)}")


if __name__ == "__main__":
    entrada = sys.argv[1] if len(sys.argv) > 1 else "entrada.txt"
    simular(entrada)
