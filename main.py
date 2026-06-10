import sys
from collections import deque

from le_dados import carregar_processos
from modelos.escalonador import Escalonador
from modelos.gerenciador import GerenciadorMemoria
from modelos.recursos import GerenciadorRecursos


def mudar_estado(processo, novo_estado, tempo):
    anterior = processo.estado
    processo.alterar_estado(novo_estado)
    print(f"[t={tempo}] Processo #{processo.pid}: {anterior} -> {novo_estado}")


def criar_processo(
    processo,
    tempo,
    memoria,
    recursos,
    escalonador,
    esperando_memoria,
    esperando_recurso,
):
    print(f"[t={tempo}] Criando Processo #{processo.pid}")

    if processo.prioridade == 0 and processo.ram > 512:
        print(
            f"[t={tempo}] ERRO: Processo #{processo.pid} tempo real solicitou {processo.ram} MiB"
        )
        return False

    if not memoria.alocar(processo):
        mudar_estado(processo, "ESPERANDO_MEMORIA", tempo)
        esperando_memoria.append(processo)
        return True

    if not recursos.alocar_discos(processo):
        mudar_estado(processo, "ESPERANDO_RECURSO", tempo)
        esperando_recurso.append(processo)
        return True

    escalonador.adicionar_processo(processo)
    print(f"[t={tempo}] Processo #{processo.pid}: NOVO -> PRONTO")
    return True


def tentar_atender_fila_memoria(
    memoria, recursos, escalonador, esperando_memoria, esperando_recurso, tempo
):
    proximos = deque()
    while esperando_memoria:
        processo = esperando_memoria.popleft()
        if memoria.alocar(processo):
            if recursos.alocar_discos(processo):
                escalonador.adicionar_processo(processo)
                print(
                    f"[t={tempo}] Processo #{processo.pid}: ESPERANDO_MEMORIA -> PRONTO"
                )
            else:
                mudar_estado(processo, "ESPERANDO_RECURSO", tempo)
                esperando_recurso.append(processo)
        else:
            processo.tempo_espera += 1
            proximos.append(processo)
    return proximos


def tentar_atender_fila_recursos(recursos, escalonador, esperando_recurso, tempo):
    proximos = deque()
    while esperando_recurso:
        processo = esperando_recurso.popleft()
        if recursos.alocar_discos(processo):
            escalonador.adicionar_processo(processo)
            print(f"[t={tempo}] Processo #{processo.pid}: ESPERANDO_RECURSO -> PRONTO")
        else:
            processo.tempo_espera += 1
            proximos.append(processo)
    return proximos


def processar_io_concluido(recursos, escalonador, tempo):
    finalizados_io = recursos.executar_ciclo()
    for processo in finalizados_io:
        escalonador.voltar_do_io(processo)
        print(
            f"[t={tempo}] Processo #{processo.pid}: BLOQUEADO -> PRONTO (retorno de I/O)"
        )


def imprimir_estado(
    tempo, escalonador, memoria, recursos, esperando_memoria, esperando_recurso
):
    print("\n" + "=" * 50)
    print(f"Tempo: {tempo}\n")
    escalonador.mostrar_escalonador()
    print("=== FILAS DE ESPERA ===")
    print(f"Esperando memoria: {[processo.pid for processo in esperando_memoria]}")
    print(f"Esperando recurso: {[processo.pid for processo in esperando_recurso]}")
    print(f"Bloqueados I/O: {[processo.pid for processo in recursos.fila_io]}")
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
    esperando_recurso = deque()

    tempo = 0
    finalizados = []

    while True:
        while fila_novos and fila_novos[0].tempo_chegada == tempo:
            processo = fila_novos.popleft()
            criar_processo(
                processo,
                tempo,
                memoria,
                recursos,
                escalonador,
                esperando_memoria,
                esperando_recurso,
            )

        esperando_memoria = tentar_atender_fila_memoria(
            memoria, recursos, escalonador, esperando_memoria, esperando_recurso, tempo
        )
        esperando_recurso = tentar_atender_fila_recursos(
            recursos, escalonador, esperando_recurso, tempo
        )

        processar_io_concluido(recursos, escalonador, tempo)

        escalonador.escalonar()
        eventos = escalonador.executar_ciclo()

        for evento, processo in eventos:
            if evento == "io":
                recursos.enviar_para_io(processo)
                print(f"[t={tempo}] Processo #{processo.pid}: EXECUTANDO -> BLOQUEADO")
            elif evento == "finalizado":
                memoria.liberar(processo.pid)
                recursos.liberar_discos(processo.pid)
                finalizados.append(processo)
                print(f"[t={tempo}] Processo #{processo.pid}: EXECUTANDO -> FINALIZADO")
            elif evento == "quantum":
                print(
                    f"[t={tempo}] Processo #{processo.pid}: EXECUTANDO -> PRONTO (quantum esgotado)"
                )
            elif evento == "pronto":
                print(f"[t={tempo}] Processo #{processo.pid}: EXECUTANDO -> PRONTO")

        imprimir_estado(
            tempo, escalonador, memoria, recursos, esperando_memoria, esperando_recurso
        )

        if (
            not fila_novos
            and not esperando_memoria
            and not esperando_recurso
            and not escalonador.tem_pendente()
            and not recursos.tem_pendente()
        ):
            break

        tempo += 1

    print(f"\nSimulação finalizada em {tempo} ciclos")
    print(f"Processos finalizados: {len(finalizados)}")
    print(
        f"Processos de tempo real: {sum(1 for p in finalizados if p.prioridade == 0)}"
    )
    print(f"Processos de usuário: {sum(1 for p in finalizados if p.prioridade == 1)}")


if __name__ == "__main__":
    entrada = sys.argv[1] if len(sys.argv) > 1 else "entrada_teste.txt"
    simular(entrada)
