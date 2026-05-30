import processo

class GerenciadorMemoria:

    MEMORIA_TOTAL = 32768

    def __init__(self):
        self.blocos = [
            {
                "inicio": 0,
                "tamanho": self.MEMORIA_TOTAL,
                "livre": True,
                "pid": None
            }
        ]


    def alocar(self, processo):
        """
                Aloca memória usando sistema de blocos.
                Retorna True se conseguiu alocar.
                Retorna False se não houver espaço.
        """
        memoria_necessaria = processo.ram
        for i, bloco in enumerate(self.blocos):

            if bloco["livre"] and bloco["tamanho"] >= memoria_necessaria:

                # Caso o bloco tenha exatamente o tamanho necessário
                if bloco["tamanho"] == memoria_necessaria:
                    bloco["livre"] = False
                    bloco["pid"] = processo.pid

                # Caso precise dividir o bloco
                else:
                    novo_bloco_livre = {
                        "inicio": bloco["inicio"] + memoria_necessaria,
                        "tamanho": bloco["tamanho"] - memoria_necessaria,
                        "livre": True,
                        "pid": None
                    }

                    bloco["tamanho"] = memoria_necessaria
                    bloco["livre"] = False
                    bloco["pid"] = processo.pid

                    self.blocos.insert(i + 1, novo_bloco_livre)

                return True

        return False


    def liberar(self, pid):
        """
        Libera a memória ocupada por um processo.
        """

        for bloco in self.blocos:

            if bloco["pid"] == pid:

                bloco["livre"] = True
                bloco["pid"] = None

                self.unir_blocos()
                return True

        return False


    def unir_blocos(self):
        """
        Une blocos livres adjacentes.
        """

        i = 0

        while i < len(self.blocos) - 1:

            atual = self.blocos[i]
            proximo = self.blocos[i + 1]

            if atual["livre"] and proximo["livre"]:

                atual["tamanho"] += proximo["tamanho"]
                self.blocos.pop(i + 1)

            else:
                i += 1


    def mostrar_memoria(self):
        """
        Exibe o estado atual da memória.
        """

        print("\n=== MEMÓRIA ===")

        for bloco in self.blocos:
            print(bloco)

        print()