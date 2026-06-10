from collections import deque

from modelos.processo import Processo


def carregar_processos(arq):
    fila_novos = deque()

    with open(arq, "r", encoding="utf-8-sig") as arquivo:
        for linha in arquivo:
            linha = linha.split("#")[0].strip()
            if linha == "":
                continue

            dados = [item.strip() for item in linha.split(",")]
            if len(dados) == 5:
                pid, cpu1, io, cpu2, ram = map(int, dados)
                processo = Processo(pid, cpu1, io, cpu2, ram)
            elif len(dados) == 8:
                pid, chegada, prioridade, cpu1, io, cpu2, ram, discos = map(int, dados)
                processo = Processo(
                    pid,
                    cpu1,
                    io,
                    cpu2,
                    ram,
                    chegada=chegada,
                    prioridade=prioridade,
                    discos_necessarios=discos,
                )
            else:
                raise ValueError(
                    f"Formato inválido na linha: '{linha}'. Esperado 5 ou 8 campos."
                )

            fila_novos.append(processo)

    return fila_novos
