import tkinter as tk
from collections import deque
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from le_dados import carregar_processos
from modelos.escalonador import Escalonador
from modelos.gerenciador import GerenciadorMemoria
from modelos.recursos import GerenciadorRecursos


COR_FUNDO = "#0f172a"
COR_PAINEL = "#111827"
COR_PAINEL_2 = "#1f2937"
COR_TEXTO = "#e5e7eb"
COR_TEXTO_FRACO = "#94a3b8"
COR_LIVRE = "#334155"
COR_CPU_TR = "#7c3aed"
COR_CPU_USUARIO = "#2563eb"
COR_DISCO = "#0f766e"
COR_ALERTA = "#b45309"
COR_OK = "#16a34a"


class InterfaceSimulador:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Sistema Operacional")
        self.root.geometry("1220x780")
        self.root.minsize(1080, 680)
        self.root.configure(bg=COR_FUNDO)

        self.arquivo_var = tk.StringVar(value="entrada.txt")
        self.velocidade_var = tk.IntVar(value=550)
        self.rodando = False
        self.finalizada = False

        self._configurar_estilo()
        self._criar_layout()
        self.reiniciar()

    def _configurar_estilo(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Horizontal.TProgressbar",
            troughcolor="#1e293b",
            background="#38bdf8",
            bordercolor="#1e293b",
            lightcolor="#38bdf8",
            darkcolor="#38bdf8",
        )

    def _criar_layout(self):
        topo = tk.Frame(self.root, bg=COR_FUNDO, padx=18, pady=14)
        topo.pack(fill="x")

        titulo = tk.Label(
            topo,
            text="Gerenciador e Escalonador de Processos",
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Segoe UI", 19, "bold"),
        )
        titulo.grid(row=0, column=0, sticky="w")

        subtitulo = tk.Label(
            topo,
            text="4 CPUs, 4 discos de I/O e memoria principal compartilhada",
            bg=COR_FUNDO,
            fg=COR_TEXTO_FRACO,
            font=("Segoe UI", 10),
        )
        subtitulo.grid(row=1, column=0, sticky="w", pady=(2, 0))

        controles = tk.Frame(topo, bg=COR_FUNDO)
        controles.grid(row=0, column=1, rowspan=2, sticky="e")
        topo.columnconfigure(0, weight=1)

        self._botao(controles, "Arquivo", self.escolher_arquivo).grid(row=0, column=0, padx=4)
        self._botao(controles, "Reiniciar", self.reiniciar).grid(row=0, column=1, padx=4)
        self._botao(controles, "Proximo ciclo", self.avancar_ciclo).grid(row=0, column=2, padx=4)
        self.botao_auto = self._botao(controles, "Executar", self.alternar_auto)
        self.botao_auto.grid(row=0, column=3, padx=4)

        self.arquivo_label = tk.Label(
            controles,
            textvariable=self.arquivo_var,
            bg=COR_FUNDO,
            fg=COR_TEXTO_FRACO,
            font=("Consolas", 9),
        )
        self.arquivo_label.grid(row=1, column=0, columnspan=4, sticky="e", pady=(8, 0))

        velocidade = tk.Frame(controles, bg=COR_FUNDO)
        velocidade.grid(row=2, column=0, columnspan=4, sticky="e", pady=(8, 0))
        tk.Label(
            velocidade,
            text="Velocidade",
            bg=COR_FUNDO,
            fg=COR_TEXTO_FRACO,
            font=("Segoe UI", 9),
        ).pack(side="left", padx=(0, 8))
        escala = tk.Scale(
            velocidade,
            from_=1000,
            to=120,
            orient="horizontal",
            length=180,
            showvalue=False,
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            troughcolor="#334155",
            highlightthickness=0,
            activebackground="#38bdf8",
            command=lambda valor: self.velocidade_var.set(int(float(valor))),
        )
        escala.set(self.velocidade_var.get())
        escala.pack(side="left")

        corpo = tk.Frame(self.root, bg=COR_FUNDO)
        corpo.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        corpo.columnconfigure(0, weight=3)
        corpo.columnconfigure(1, weight=1)
        corpo.rowconfigure(0, weight=1)

        painel_esquerdo = tk.Frame(corpo, bg=COR_FUNDO)
        painel_esquerdo.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        painel_esquerdo.columnconfigure(0, weight=1)
        painel_esquerdo.rowconfigure(3, weight=1)

        painel_log = self._painel(corpo, "Eventos")
        painel_log.grid(row=0, column=1, sticky="nsew")
        painel_log.rowconfigure(1, weight=1)
        painel_log.columnconfigure(0, weight=1)

        self.log_texto = tk.Text(
            painel_log,
            bg="#020617",
            fg=COR_TEXTO,
            insertbackground=COR_TEXTO,
            relief="flat",
            wrap="word",
            font=("Consolas", 9),
            width=42,
            padx=10,
            pady=10,
        )
        self.log_texto.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        rolagem = tk.Scrollbar(painel_log, command=self.log_texto.yview)
        rolagem.grid(row=1, column=1, sticky="ns", pady=(0, 12), padx=(0, 12))
        self.log_texto.configure(yscrollcommand=rolagem.set)

        self._criar_resumo(painel_esquerdo)
        self._criar_recursos(painel_esquerdo)
        self._criar_filas(painel_esquerdo)
        self._criar_memoria(painel_esquerdo)

    def _botao(self, parent, texto, comando):
        return tk.Button(
            parent,
            text=texto,
            command=comando,
            bg="#e5e7eb",
            fg="#111827",
            activebackground="#cbd5e1",
            activeforeground="#111827",
            relief="flat",
            padx=12,
            pady=7,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )

    def _painel(self, parent, titulo):
        painel = tk.Frame(parent, bg=COR_PAINEL, highlightthickness=1, highlightbackground="#243244")
        tk.Label(
            painel,
            text=titulo,
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            padx=12,
            pady=10,
        ).grid(row=0, column=0, sticky="ew")
        return painel

    def _criar_resumo(self, parent):
        painel = tk.Frame(parent, bg=COR_FUNDO)
        painel.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for coluna in range(5):
            painel.columnconfigure(coluna, weight=1)

        self.cards_resumo = {}
        itens = [
            ("tempo", "Tempo"),
            ("finalizados", "Finalizados"),
            ("tempo_real", "Tempo real"),
            ("usuarios", "Usuarios"),
            ("memoria", "Memoria usada"),
        ]

        for coluna, (chave, titulo) in enumerate(itens):
            card = tk.Frame(painel, bg=COR_PAINEL_2, padx=12, pady=10, height=74)
            card.grid(row=0, column=coluna, sticky="ew", padx=(0 if coluna == 0 else 8, 0))
            card.grid_propagate(False)
            tk.Label(card, text=titulo, bg=COR_PAINEL_2, fg=COR_TEXTO_FRACO, font=("Segoe UI", 9)).pack(anchor="w")
            valor = tk.Label(
                card,
                text="0",
                bg=COR_PAINEL_2,
                fg=COR_TEXTO,
                font=("Segoe UI", 18, "bold"),
                width=12,
                anchor="w",
            )
            valor.pack(anchor="w", pady=(4, 0))
            self.cards_resumo[chave] = valor

    def _criar_recursos(self, parent):
        painel = tk.Frame(parent, bg=COR_FUNDO)
        painel.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        painel.columnconfigure(0, weight=1)
        painel.columnconfigure(1, weight=1)

        painel_cpus = self._painel(painel, "CPUs")
        painel_cpus.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        for coluna in range(4):
            painel_cpus.columnconfigure(coluna, weight=1)

        painel_discos = self._painel(painel, "Discos de I/O")
        painel_discos.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        for coluna in range(4):
            painel_discos.columnconfigure(coluna, weight=1)

        self.cpu_cards = []
        self.disco_cards = []

        for i in range(4):
            self.cpu_cards.append(self._card_recurso(painel_cpus, 1, i, f"CPU {i}"))
            self.disco_cards.append(self._card_recurso(painel_discos, 1, i, f"Disco {i}"))

    def _card_recurso(self, parent, linha, coluna, titulo):
        frame = tk.Frame(parent, bg=COR_LIVRE, width=142, height=96, padx=10, pady=9)
        frame.grid(row=linha, column=coluna, sticky="ew", padx=6, pady=(0, 12))
        frame.grid_propagate(False)

        label_titulo = tk.Label(
            frame,
            text=titulo,
            bg=COR_LIVRE,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            width=14,
            anchor="w",
        )
        label_titulo.grid(row=0, column=0, sticky="ew")

        label_info = tk.Label(
            frame,
            text="Livre",
            bg=COR_LIVRE,
            fg="white",
            justify="left",
            font=("Segoe UI", 9),
            width=18,
            height=3,
            anchor="nw",
            wraplength=118,
        )
        label_info.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        frame.columnconfigure(0, weight=1)

        return frame, label_titulo, label_info

    def _criar_filas(self, parent):
        painel = self._painel(parent, "Filas")
        painel.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        for coluna in range(3):
            painel.columnconfigure(coluna, weight=1)

        self.labels_filas = {}
        nomes = [
            ("tr", "Tempo real"),
            ("u1", "Usuario F1"),
            ("u2", "Usuario F2"),
            ("u3", "Usuario F3"),
            ("io", "Fila I/O"),
            ("mem", "Espera memoria"),
        ]

        for indice, (chave, titulo) in enumerate(nomes):
            linha = 1 + indice // 3
            coluna = indice % 3
            bloco = tk.Frame(painel, bg=COR_PAINEL_2, height=68, padx=10, pady=8)
            bloco.grid(row=linha, column=coluna, sticky="ew", padx=8, pady=(0, 10))
            bloco.grid_propagate(False)
            tk.Label(
                bloco,
                text=titulo,
                bg=COR_PAINEL_2,
                fg=COR_TEXTO_FRACO,
                font=("Segoe UI", 9),
                anchor="w",
            ).grid(row=0, column=0, sticky="ew")
            valor = tk.Label(
                bloco,
                text="[]",
                bg=COR_PAINEL_2,
                fg=COR_TEXTO,
                font=("Consolas", 10),
                width=28,
                height=2,
                anchor="nw",
                justify="left",
                wraplength=230,
            )
            valor.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
            bloco.columnconfigure(0, weight=1)
            self.labels_filas[chave] = valor

    def _criar_memoria(self, parent):
        painel = self._painel(parent, "Memoria por blocos")
        painel.grid(row=3, column=0, sticky="nsew")
        painel.columnconfigure(0, weight=1)
        painel.rowconfigure(2, weight=1)

        self.memoria_progress = ttk.Progressbar(painel, style="Horizontal.TProgressbar", maximum=100)
        self.memoria_progress.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        self.memoria_canvas = tk.Canvas(
            painel,
            bg="#020617",
            highlightthickness=0,
            height=210,
        )
        self.memoria_canvas.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.memoria_canvas.bind("<Configure>", lambda _evento: self.atualizar_memoria())

    def escolher_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Escolher entrada",
            initialdir=Path.cwd(),
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
        )
        if caminho:
            self.arquivo_var.set(caminho)
            self.reiniciar()

    def reiniciar(self):
        try:
            self.fila_novos = carregar_processos(self.arquivo_var.get())
        except Exception as erro:
            messagebox.showerror("Erro ao carregar entrada", str(erro))
            return

        self.fila_novos = deque(sorted(self.fila_novos, key=lambda p: (p.tempo_chegada, p.pid)))
        self.memoria = GerenciadorMemoria()
        self.recursos = GerenciadorRecursos()
        self.escalonador = Escalonador()
        self.esperando_memoria = deque()
        self.finalizados = []
        self.rejeitados = []
        self.tempo = 0
        self.rodando = False
        self.finalizada = False
        self.botao_auto.configure(text="Executar")
        self.log_texto.delete("1.0", "end")
        self.log("Simulacao carregada.")
        self.atualizar_interface()

    def log(self, mensagem):
        self.log_texto.insert("end", mensagem + "\n")
        self.log_texto.see("end")

    def criar_processo(self, processo):
        self.log(f"[t={self.tempo}] Criando Processo #{processo.pid}")

        if processo.prioridade == 0 and processo.ram > 512:
            self.log(f"[t={self.tempo}] ERRO: Processo #{processo.pid} tempo real solicitou {processo.ram} MiB")
            self.rejeitados.append(processo)
            return

        if processo.prioridade == 0 and (processo.io > 0 or processo.cpu2 > 0):
            self.log(f"[t={self.tempo}] ERRO: Processo #{processo.pid} tempo real nao pode usar I/O")
            self.rejeitados.append(processo)
            return

        if not self.memoria.alocar(processo):
            anterior = processo.estado
            processo.alterar_estado("ESPERANDO_MEMORIA")
            self.esperando_memoria.append(processo)
            self.log(f"[t={self.tempo}] Processo #{processo.pid}: {anterior} -> ESPERANDO_MEMORIA")
            return

        anterior = processo.estado
        self.escalonador.adicionar_processo(processo)
        self.log(f"[t={self.tempo}] Processo #{processo.pid}: {anterior} -> PRONTO")

    def tentar_atender_memoria(self):
        proximos = deque()

        while self.esperando_memoria:
            processo = self.esperando_memoria.popleft()

            if self.memoria.alocar(processo):
                anterior = processo.estado
                self.escalonador.adicionar_processo(processo)
                self.log(f"[t={self.tempo}] Processo #{processo.pid}: {anterior} -> PRONTO")
            else:
                processo.tempo_espera += 1
                proximos.append(processo)

        self.esperando_memoria = proximos

    def escalonar_processos_prontos(self):
        for evento, processo in self.escalonador.escalonar():
            if evento == "preemptado":
                self.log(f"[t={self.tempo}] Processo #{processo.pid}: EXECUTANDO -> PRONTO (preemptado por tempo real)")

    def avancar_ciclo(self):
        if self.finalizada:
            return

        while self.fila_novos and self.fila_novos[0].tempo_chegada == self.tempo:
            self.criar_processo(self.fila_novos.popleft())

        self.escalonar_processos_prontos()

        for evento, processo in self.escalonador.executar_ciclo():
            if evento == "io":
                self.recursos.enviar_para_io(processo)
                self.log(f"[t={self.tempo}] Processo #{processo.pid}: EXECUTANDO -> BLOQUEADO")
            elif evento == "finalizado":
                self.memoria.liberar(processo.pid)
                self.finalizados.append(processo)
                self.log(f"[t={self.tempo}] Processo #{processo.pid}: EXECUTANDO -> FINALIZADO")
            elif evento == "quantum":
                self.log(f"[t={self.tempo}] Processo #{processo.pid}: EXECUTANDO -> PRONTO (quantum esgotado)")
            elif evento == "pronto":
                self.log(f"[t={self.tempo}] Processo #{processo.pid}: EXECUTANDO -> PRONTO")

        for processo in self.recursos.executar_ciclo():
            self.escalonador.voltar_do_io(processo)
            self.log(f"[t={self.tempo}] Processo #{processo.pid}: BLOQUEADO -> PRONTO (retorno de I/O)")

        self.tentar_atender_memoria()
        self.escalonar_processos_prontos()
        self.atualizar_interface()

        if self.simulacao_terminou():
            self.finalizar_simulacao()
        else:
            self.tempo += 1

    def simulacao_terminou(self):
        return (
            not self.fila_novos
            and not self.esperando_memoria
            and not self.escalonador.tem_pendente()
            and not self.recursos.tem_pendente()
        )

    def finalizar_simulacao(self):
        self.finalizada = True
        self.rodando = False
        self.botao_auto.configure(text="Executar")
        self.log("")
        self.log(f"Simulacao finalizada em {self.tempo} ciclos")
        self.log(f"Processos finalizados: {len(self.finalizados)}")
        self.log(f"Processos rejeitados: {len(self.rejeitados)}")
        self.log(f"Tempo real: {sum(1 for p in self.finalizados if p.prioridade == 0)}")
        self.log(f"Usuarios: {sum(1 for p in self.finalizados if p.prioridade == 1)}")
        self.atualizar_interface()

    def alternar_auto(self):
        if self.finalizada:
            return

        self.rodando = not self.rodando
        self.botao_auto.configure(text="Pausar" if self.rodando else "Executar")

        if self.rodando:
            self.executar_auto()

    def executar_auto(self):
        if not self.rodando or self.finalizada:
            return

        self.avancar_ciclo()
        self.root.after(self.velocidade_var.get(), self.executar_auto)

    def atualizar_interface(self):
        self.atualizar_resumo()
        self.atualizar_cpus()
        self.atualizar_discos()
        self.atualizar_filas()
        self.atualizar_memoria()

    def atualizar_resumo(self):
        usada = self.memoria_usada()
        self.cards_resumo["tempo"].configure(text=str(self.tempo))
        self.cards_resumo["finalizados"].configure(text=str(len(self.finalizados)))
        self.cards_resumo["tempo_real"].configure(text=str(sum(1 for p in self.finalizados if p.prioridade == 0)))
        self.cards_resumo["usuarios"].configure(text=str(sum(1 for p in self.finalizados if p.prioridade == 1)))
        self.cards_resumo["memoria"].configure(text=f"{usada} MiB")
        self.memoria_progress["value"] = usada / self.memoria.MEMORIA_TOTAL * 100

    def atualizar_cpus(self):
        for i, processo in enumerate(self.escalonador.cpus):
            if processo is None:
                self._atualizar_card(self.cpu_cards[i], COR_LIVRE, f"CPU {i}", "Livre")
                continue

            cor = COR_CPU_TR if processo.prioridade == 0 else COR_CPU_USUARIO
            tipo = "Tempo real" if processo.prioridade == 0 else f"Usuario F{processo.fila_feedback}"
            restante = processo.tempo_restante_fase()
            texto = f"#{processo.pid}  {tipo}\n{processo.obter_fase()} - {restante} u.t."
            if processo.prioridade == 1:
                texto += f"\nQuantum {processo.quantum_usado}/2"
            self._atualizar_card(self.cpu_cards[i], cor, f"CPU {i}", texto)

    def atualizar_discos(self):
        for i, processo in enumerate(self.recursos.discos):
            if processo is None:
                self._atualizar_card(self.disco_cards[i], COR_LIVRE, f"Disco {i}", "Livre")
            else:
                texto = f"Processo #{processo.pid}\nI/O restante: {processo.io_restante} u.t."
                self._atualizar_card(self.disco_cards[i], COR_DISCO, f"Disco {i}", texto)

    def _atualizar_card(self, card, cor, titulo, texto):
        frame, label_titulo, label_info = card
        frame.configure(bg=cor)
        label_titulo.configure(bg=cor, text=titulo)
        label_info.configure(bg=cor, text=texto)

    def atualizar_filas(self):
        self.labels_filas["tr"].configure(text=self._ids(self.escalonador.fila_tempo_real))
        self.labels_filas["u1"].configure(text=self._ids(self.escalonador.fila_usuario_1))
        self.labels_filas["u2"].configure(text=self._ids(self.escalonador.fila_usuario_2))
        self.labels_filas["u3"].configure(text=self._ids(self.escalonador.fila_usuario_3))
        self.labels_filas["io"].configure(text=self._ids(self.recursos.fila_io))
        self.labels_filas["mem"].configure(text=self._ids(self.esperando_memoria))

    def atualizar_memoria(self):
        canvas = self.memoria_canvas
        canvas.delete("all")

        largura = max(canvas.winfo_width(), 1)
        altura = max(canvas.winfo_height(), 1)
        x = 0

        for bloco in self.memoria.blocos:
            proporcao = bloco["tamanho"] / self.memoria.MEMORIA_TOTAL
            largura_bloco = max(1, int(largura * proporcao))
            cor = "#38bdf8" if not bloco["livre"] else "#1e293b"
            canvas.create_rectangle(x, 0, x + largura_bloco, altura, fill=cor, outline="#0f172a")

            if largura_bloco > 70:
                texto = "Livre" if bloco["livre"] else f"P{bloco['pid']}"
                texto += f"\n{bloco['tamanho']} MiB"
                canvas.create_text(
                    x + largura_bloco / 2,
                    altura / 2,
                    text=texto,
                    fill=COR_TEXTO,
                    font=("Segoe UI", 9, "bold"),
                )

            x += largura_bloco

    def memoria_usada(self):
        return sum(bloco["tamanho"] for bloco in self.memoria.blocos if not bloco["livre"])

    def _ids(self, fila):
        ids = [f"#{processo.pid}" for processo in fila]
        if not ids:
            return "[]"

        limite = 8
        if len(ids) > limite:
            visiveis = ", ".join(ids[:limite])
            return f"[{visiveis}, +{len(ids) - limite}]"

        return "[" + ", ".join(ids) + "]"


def main():
    root = tk.Tk()
    InterfaceSimulador(root)
    root.mainloop()


if __name__ == "__main__":
    main()
