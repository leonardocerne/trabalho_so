import random

class Processo:
    ESTADOS = {
        "NOVO",
        "PRONTO",
        "EXECUTANDO",
        "BLOQUEADO",
        "FINALIZADO",
        "ESPERANDO_MEMORIA",
        "ESPERANDO_RECURSO",
        "BLOQUEADO-SUSPENSO",
        "PRONTO-SUSPENSO"
    }

    def __init__(self, pid, cpu1, io, cpu2, ram, chegada=0, prioridade=None, discos_necessarios=0):
        self.pid = pid
        self.tempo_chegada = chegada
        if prioridade is not None:
            self.prioridade = prioridade
        elif ram <= 512 and io == 0 and cpu2 == 0:
            self.prioridade = random.choice([0, 1])
        else:
            self.prioridade = 1
        self.cpu1 = cpu1
        self.io = io
        self.cpu2 = cpu2
        self.ram = ram
        self.discos_necessarios = discos_necessarios
        self.estado = "NOVO"

        self.cpu1_restante = cpu1
        self.io_restante = io
        self.cpu2_restante = cpu2

        self.fila_feedback = 0
        self.fase = 1
        self.quantum_usado = 0
        self.em_io = False
        self.tempo_espera = 0

    def obter_fase(self):
        fases = {
            1: "CPU1",
            2: "IO",
            3: "CPU2",
            4: "FINALIZADO"
        }
        return fases[self.fase]

    def tempo_restante_fase(self):
        if self.fase == 1:
            return self.cpu1_restante
        if self.fase == 2:
            return self.io_restante
        if self.fase == 3:
            return self.cpu2_restante
        return 0

    def terminou(self):
        return self.fase == 4

    def alterar_estado(self, novo_estado):
        if novo_estado not in self.ESTADOS:
            raise ValueError("Estado inválido")
        self.estado = novo_estado

    def avancar_fase(self):
        if self.fase == 1:
            self.fase = 2
        elif self.fase == 2:
            self.fase = 3
        elif self.fase == 3:
            self.fase = 4
            self.estado = "FINALIZADO"

    def __repr__(self):
        return (
            f"<Processo #{self.pid} chegada={self.tempo_chegada} prioridade={self.prioridade} "
            f"fase={self.obter_fase()} estado={self.estado}>"
        )
