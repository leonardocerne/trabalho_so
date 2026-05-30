import random

class Processo:
    ESTADOS = {
        "NOVO",
        "PRONTO",
        "EXECUTANDO",
        "BLOQUEADO",
        "FINALIZADO",
        "BLOQUEADO-SUSPENSO",
        "PRONTO-SUSPENSO"
    }
    def __init__(self, pid, cpu1, io, cpu2, ram):
        self.pid = pid
        self.cpu1 = cpu1
        self.io = io
        self.cpu2 = cpu2
        self.ram = ram
        self.estado = "NOVO"
        
        self.cpu1_restante = cpu1
        self.io_restante = io           # PARA FACILITAR EXECUÇÃO
        self.cpu2_restante = cpu2

        if self.ram <= 512:
            self.prioridade = random.choice([0, 1])     # Garantir randomicidade na prioridade
        else:
            self.prioridade = 1

        self.fila_feedback = 0  # Saber em qual fila do feedback

        self.fase = 1   # Saber em qual fase de cpu

        self.quantum_usado = 0  # Para saber quanto do quantum foi usado, para o caso de precisar bloquear o processo

        ###
        #self.tempo_chegada
        #self.discos_necessarios
        ####

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