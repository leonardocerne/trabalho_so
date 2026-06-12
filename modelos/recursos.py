from collections import deque


class GerenciadorRecursos:
    def __init__(self):
        self.discos = [None, None, None, None]
        self.fila_io = deque()

    def enviar_para_io(self, processo):
        if processo.io_restante <= 0:
            return False

        processo.alterar_estado("BLOQUEADO")
        processo.quantum_usado = 0
        self.fila_io.append(processo)
        return True

    def executar_ciclo(self):
        finalizados_io = []

        for i in range(len(self.discos)):
            if self.discos[i] is None and self.fila_io:
                processo = self.fila_io.popleft()
                processo.em_io = True
                self.discos[i] = processo

        for i, processo in enumerate(self.discos):
            if processo is None:
                continue

            processo.io_restante -= 1
            if processo.io_restante <= 0:
                processo.em_io = False
                self.discos[i] = None
                finalizados_io.append(processo)

        return finalizados_io

    def tem_pendente(self):
        return bool(self.fila_io) or any(processo is not None for processo in self.discos)

    def ids_bloqueados(self):
        ids = [processo.pid for processo in self.fila_io]
        ids += [processo.pid for processo in self.discos if processo is not None]
        return ids

    def mostrar_recursos(self):
        print("\n=== DISCOS ===")

        for i, processo in enumerate(self.discos):
            if processo is None:
                print(f"Disco {i}: Livre")
            else:
                print(f"Disco {i}: Processo #{processo.pid} ({processo.io_restante} u.t. restantes)")

        fila = [processo.pid for processo in self.fila_io]
        usados = sum(1 for processo in self.discos if processo is not None)

        print(f"Fila de I/O: {fila}")
        print(f"Discos usados: {usados} / 4")
        print()
