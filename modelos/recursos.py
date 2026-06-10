from collections import deque


class GerenciadorRecursos:
    def __init__(self):
        self.discos = [None, None, None, None]
        self.fila_io = deque()

    def contar_discos_livres(self):
        return sum(1 for disco in self.discos if disco is None)

    def alocar_discos(self, processo):
        if processo.discos_necessarios <= 0:
            return True

        if processo.prioridade == 0 and processo.discos_necessarios > 0:
            return False

        disponiveis = self.contar_discos_livres()
        if disponiveis < processo.discos_necessarios:
            return False

        alocados = 0
        for i in range(len(self.discos)):
            if self.discos[i] is None:
                self.discos[i] = processo
                alocados += 1
                if alocados == processo.discos_necessarios:
                    break

        return True

    def liberar_discos(self, pid):
        liberou = False
        for i, processo in enumerate(self.discos):
            if processo is not None and processo.pid == pid:
                self.discos[i] = None
                liberou = True
        return liberou

    def enviar_para_io(self, processo):
        if processo.io_restante <= 0:
            return False

        processo.alterar_estado("BLOQUEADO")
        processo.quantum_usado = 0
        processo.em_io = True
        self.fila_io.append(processo)
        return True

    def executar_ciclo(self):
        finalizados_io = []
        processos_atual = list(self.fila_io)
        self.fila_io.clear()

        for processo in processos_atual:
            processo.io_restante -= 1
            if processo.io_restante <= 0:
                processo.em_io = False
                finalizados_io.append(processo)
            else:
                self.fila_io.append(processo)

        return finalizados_io

    def tem_pendente(self):
        return bool(self.fila_io)

    def mostrar_recursos(self):
        print("\n=== DISCOS ===")

        for i, processo in enumerate(self.discos):
            if processo is None:
                print(f"Disco {i}: Livre")
            else:
                status = "em I/O" if processo.em_io else "reservado"
                print(f"Disco {i}: Processo #{processo.pid} ({status})")

        fila = [processo.pid for processo in self.fila_io]
        usados = sum(1 for processo in self.discos if processo is not None)

        print(f"Fila de I/O: {fila}")
        print(f"Discos usados: {usados} / 4")
        print()
