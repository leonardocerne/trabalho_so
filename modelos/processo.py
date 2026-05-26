import random

class Processo:
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