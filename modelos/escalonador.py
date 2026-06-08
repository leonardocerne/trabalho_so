from collections import deque


class Escalonador:
    QUANTUM = 2

    def __init__(self):
        self.cpus = [None, None, None, None]
        self.fila_tempo_real = deque()
        self.fila_usuario_1 = deque()
        self.fila_usuario_2 = deque()
        self.fila_usuario_3 = deque()

    def adicionar_processo(self, processo):
        processo.alterar_estado("PRONTO")

        if processo.prioridade == 0:
            self.fila_tempo_real.append(processo)
        else:
            processo.fila_feedback = 1
            self.fila_usuario_1.append(processo)

    def voltar_do_io(self, processo):
        processo.avancar_fase()
        processo.fila_feedback = 1
        processo.quantum_usado = 0
        processo.alterar_estado("PRONTO")
        self.fila_usuario_1.append(processo)

    def escolher_processo(self):
        if self.fila_tempo_real:
            return self.fila_tempo_real.popleft()

        if self.fila_usuario_1:
            return self.fila_usuario_1.popleft()

        if self.fila_usuario_2:
            return self.fila_usuario_2.popleft()

        if self.fila_usuario_3:
            return self.fila_usuario_3.popleft()

        return None

    def finalizar_processo(self, processo):
        processo.fase = 4
        processo.alterar_estado("FINALIZADO")

    def escalonar(self):
        for i in range(len(self.cpus)):
            if self.cpus[i] is not None:
                continue

            processo = self.escolher_processo()

            if processo is None:
                continue

            processo.alterar_estado("EXECUTANDO")
            self.cpus[i] = processo

    def executar_ciclo(self):
        eventos = []

        for i, processo in enumerate(self.cpus):
            if processo is None:
                continue

            if processo.fase == 1:
                processo.cpu1_restante -= 1
            elif processo.fase == 3:
                processo.cpu2_restante -= 1

            if processo.prioridade == 1:
                processo.quantum_usado += 1

            if processo.tempo_restante_fase() <= 0:
                self.cpus[i] = None
                processo.quantum_usado = 0

                if processo.fase == 1 and processo.io_restante > 0:
                    processo.avancar_fase()
                    eventos.append(("io", processo))
                else:
                    self.finalizar_processo(processo)
                    eventos.append(("finalizado", processo))

            elif processo.prioridade == 1 and processo.quantum_usado == self.QUANTUM:
                self.cpus[i] = None
                processo.quantum_usado = 0
                processo.alterar_estado("PRONTO")

                if processo.fila_feedback == 1:
                    processo.fila_feedback = 2
                    self.fila_usuario_2.append(processo)
                else:
                    processo.fila_feedback = 3
                    self.fila_usuario_3.append(processo)

                eventos.append(("quantum", processo))

        return eventos

    def tem_pendente(self):
        return (
            any(processo is not None for processo in self.cpus)
            or bool(self.fila_tempo_real)
            or bool(self.fila_usuario_1)
            or bool(self.fila_usuario_2)
            or bool(self.fila_usuario_3)
        )

    def mostrar_escalonador(self):
        print("\n=== CPUs ===")

        for i, processo in enumerate(self.cpus):
            if processo is None:
                print(f"CPU {i}: Livre")
            else:
                tipo = "Tempo real" if processo.prioridade == 0 else f"Usuario Fila {processo.fila_feedback}"
                print(f"CPU {i}: Processo #{processo.pid} - {tipo}")

        print("\n=== FILAS DE PRONTOS ===")
        print(f"Tempo real: {[processo.pid for processo in self.fila_tempo_real]}")
        print(f"Usuario F1: {[processo.pid for processo in self.fila_usuario_1]}")
        print(f"Usuario F2: {[processo.pid for processo in self.fila_usuario_2]}")
        print(f"Usuario F3: {[processo.pid for processo in self.fila_usuario_3]}")
        print()
