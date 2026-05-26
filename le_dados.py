from collections import deque
from modelos.processo import Processo

def carregar_processos(arq):
    fila_novos = deque()

    with open(arq, "r") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha == "":
                continue

            dados = linha.split(",")

            pid, cpu1, io, cpu2, ram = map(int, dados)
            processo = Processo(pid, cpu1, io, cpu2, ram)
            fila_novos.append(processo)
            
    return fila_novos