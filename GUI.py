
import customtkinter as ctk
import json
import csv
import datetime as dt
from pathlib import Path

COR_BG = "#0A0E14"           
COR_BG_SECUNDARIO = "#0D1520"  
COR_SIDEBAR = "#080B10"       
COR_ACCENT = "#00D9FF"        
COR_ACCENT_HOVER = "#00A8CC"   
COR_TEXTO = "#E6E6E6"         
COR_TEXTO_DIM = "#5E6B78"      
COR_ERRO = "#FF4D4D"
COR_SUCESSO = "#4DEEEA"
COR_BORDA = "#0F3440"          

FONTE_TITULO = ("Consolas", 26, "bold")
FONTE_SUBTITULO = ("Consolas", 15, "bold")
FONTE_TEXTO = ("Consolas", 13)
FONTE_PEQUENA = ("Consolas", 11)

ctk.set_appearance_mode("dark")

RPE_OPCOES = ["Peso/Aquecimento", "Moderado/Pesado", "Difícil", "Muito Difícil", "Esforço máximo/Falha"]
OBS_OPCOES = ["Aquecimento", "Normal", "Falha", "RestPause", "Roubado"]

BASE_DIR = Path.cwd()
DIR_ARQUIVOS = BASE_DIR / "arquivos"

# Persistencia

def pasta_usuario(usuario):
    return DIR_ARQUIVOS / usuario


def usuario_existe(usuario):
    return pasta_usuario(usuario).exists()


def criar_pasta_usuario(usuario):
    pasta_usuario(usuario).mkdir(parents=True, exist_ok=True)


def carregar_json(usuario, nome_arquivo):
    caminho = pasta_usuario(usuario).joinpath(nome_arquivo)
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def salvar_json(usuario, nome_arquivo, conteudo):
    caminho = pasta_usuario(usuario).joinpath(nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(conteudo, arquivo, ensure_ascii=False, indent=4)


def salvar_csv(usuario, treinos_adicionados):
    caminho = pasta_usuario(usuario).joinpath("treinos.csv")
    linhas = []
    for tipo_treino in treinos_adicionados:
        for exercicio in treinos_adicionados[tipo_treino]:
            for sessao in treinos_adicionados[tipo_treino][exercicio]:
                total_series = len(sessao["series"])
                for serie in sessao["series"]:
                    linhas.append([
                        tipo_treino, exercicio, sessao["data"], total_series,
                        serie["serie"], serie["carga"], serie["reps"],
                        serie["rpe"], serie["obs"],
                    ])
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(["tipo_treino", "nome_exercicio", "data", "series_totais",
                          "serie", "carga", "reps", "rpe", "obs"])
        writer.writerows(linhas)


def salvar_tudo(usuario, treinos_adicionados, exercicios_adicionados):
    criar_pasta_usuario(usuario)
    salvar_json(usuario, "exercicios.json", exercicios_adicionados)
    salvar_json(usuario, "treinos.json", treinos_adicionados)
    salvar_csv(usuario, treinos_adicionados)


# Classe App
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MyGym")
        self.geometry("1000x650")
        self.configure(fg_color=COR_BG)
        self.minsize(900, 600)

        self.usuario = None
        self.treinos_adicionados = {}
        self.exercicios_adicionados = {}

        self.serie_atual = 1
        self.sessao_treino_ativa = None

        self.tela_inicial()

    def limpar_janela(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_mensagem(self, label_widget, texto, sucesso=False):
        cor = COR_SUCESSO if sucesso else COR_ERRO
        label_widget.configure(text=texto, text_color=cor)

    def tela_inicial(self):
        self.limpar_janela()

        container = ctk.CTkFrame(self, fg_color=COR_BG)
        container.pack(expand=True, fill="both")

        titulo = ctk.CTkLabel(container, text="MYGYM", font=FONTE_TITULO, text_color=COR_ACCENT)
        titulo.place(relx=0.5, rely=0.32, anchor="center")

        subtitulo = ctk.CTkLabel(container, text="Diário de treino", font=FONTE_TEXTO, text_color=COR_TEXTO_DIM)
        subtitulo.place(relx=0.5, rely=0.4, anchor="center")

        btn_carregar = ctk.CTkButton(
            container, text="Carregar Dados", font=FONTE_SUBTITULO,
            fg_color=COR_BG_SECUNDARIO, hover_color=COR_ACCENT_HOVER,
            border_width=2, border_color=COR_ACCENT, text_color=COR_ACCENT,
            width=220, height=45, corner_radius=6,
            command=self.tela_input_usuario_carregar,
        )
        btn_carregar.place(relx=0.5, rely=0.52, anchor="center")

        btn_novo = ctk.CTkButton(
            container, text="Novo Usuário", font=FONTE_SUBTITULO,
            fg_color=COR_ACCENT, hover_color=COR_ACCENT_HOVER,
            text_color=COR_BG, width=220, height=45, corner_radius=6,
            command=self.tela_input_usuario_novo,
        )
        btn_novo.place(relx=0.5, rely=0.6, anchor="center")

    def _tela_input_usuario(self, titulo_texto, ao_confirmar):
        """Tela genérica que pede um nome de usuário e chama ao_confirmar(nome)."""
        self.limpar_janela()
        container = ctk.CTkFrame(self, fg_color=COR_BG)
        container.pack(expand=True, fill="both")

        ctk.CTkLabel(container, text=titulo_texto, font=FONTE_SUBTITULO,
                     text_color=COR_ACCENT).place(relx=0.5, rely=0.35, anchor="center")

        entrada = ctk.CTkEntry(container, width=260, font=FONTE_TEXTO,
                                fg_color=COR_BG_SECUNDARIO, border_color=COR_ACCENT,
                                text_color=COR_TEXTO, placeholder_text="Nome de usuário")
        entrada.place(relx=0.5, rely=0.45, anchor="center")
        entrada.focus()

        label_erro = ctk.CTkLabel(container, text="", font=FONTE_PEQUENA)
        label_erro.place(relx=0.5, rely=0.52, anchor="center")

        def confirmar():
            nome = entrada.get().strip()
            if not nome:
                self.mostrar_mensagem(label_erro, "[!] Digite um nome de usuário.")
                return
            ao_confirmar(nome, label_erro)

        btn_confirmar = ctk.CTkButton(
            container, text="Confirmar", font=FONTE_TEXTO,
            fg_color=COR_ACCENT, hover_color=COR_ACCENT_HOVER, text_color=COR_BG,
            width=160, command=confirmar,
        )
        btn_confirmar.place(relx=0.5, rely=0.6, anchor="center")
        entrada.bind("<Return>", lambda evento: confirmar())

        btn_voltar = ctk.CTkButton(
            container, text="< Voltar", font=FONTE_PEQUENA,
            fg_color="transparent", hover_color=COR_BG_SECUNDARIO,
            text_color=COR_TEXTO_DIM, width=100,
            command=self.tela_inicial,
        )
        btn_voltar.place(relx=0.5, rely=0.68, anchor="center")

    def tela_input_usuario_carregar(self):
        def ao_confirmar(nome, label_erro):
            if not usuario_existe(nome):
                self.mostrar_mensagem(label_erro, f"[!] Usuário '{nome}' não encontrado.")
                return
            self.usuario = nome
            self.exercicios_adicionados = carregar_json(nome, "exercicios.json")
            self.treinos_adicionados = carregar_json(nome, "treinos.json")
            self.tela_principal()

        self._tela_input_usuario("Digite seu nome de usuário", ao_confirmar)

    def tela_input_usuario_novo(self):
        def ao_confirmar(nome, label_erro):
            if usuario_existe(nome):
                self.mostrar_mensagem(label_erro, f"[!] O usuário '{nome}' já existe. Use 'Carregar Dados'.")
                return
            criar_pasta_usuario(nome)
            self.usuario = nome
            self.exercicios_adicionados = {}
            self.treinos_adicionados = {}
            self.tela_principal()

        self._tela_input_usuario("Escolha um nome de usuário", ao_confirmar)

    def tela_principal(self):
        self.limpar_janela()

        # --- Sidebar (esquerda) ---
        sidebar = ctk.CTkFrame(self, fg_color=COR_SIDEBAR, width=220, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="MYGYM", font=FONTE_TITULO, text_color=COR_ACCENT).pack(pady=(30, 5))
        ctk.CTkLabel(sidebar, text=dt.datetime.now().strftime("%d-%m-%Y"),
                     font=FONTE_PEQUENA, text_color=COR_TEXTO_DIM).pack(pady=(0, 2))
        ctk.CTkLabel(sidebar, text=f"Usuário: {self.usuario}",
                     font=FONTE_PEQUENA, text_color=COR_TEXTO_DIM).pack(pady=(0, 25))

        separador = ctk.CTkFrame(sidebar, fg_color=COR_BORDA, height=2)
        separador.pack(fill="x", padx=15, pady=(0, 15))

        botoes_nav = [
            ("Início", self.secao_inicio),
            ("Exercícios", self.secao_exercicios),
            ("Treino", self.secao_treino),
            ("Consulta", self.secao_consulta),
            ("Estatística", self.secao_estatistica),
            ("Ajuda", self.secao_ajuda),
        ]
        for texto, comando in botoes_nav:
            btn = ctk.CTkButton(
                sidebar, text=texto, font=FONTE_TEXTO, anchor="w",
                fg_color="transparent", hover_color=COR_BG_SECUNDARIO,
                text_color=COR_TEXTO, corner_radius=6, height=38,
                command=comando,
            )
            btn.pack(fill="x", padx=15, pady=3)

        btn_sair = ctk.CTkButton(
            sidebar, text="Sair", font=FONTE_TEXTO,
            fg_color="transparent", hover_color=COR_ERRO,
            text_color=COR_ERRO, corner_radius=6, height=38,
            command=self.sair,
        )
        btn_sair.pack(fill="x", padx=15, pady=(30, 15), side="bottom")

        # --- Área de conteúdo (direita) ---
        self.area_conteudo = ctk.CTkFrame(self, fg_color=COR_BG)
        self.area_conteudo.pack(side="left", fill="both", expand=True)

        self.secao_inicio()

    def limpar_conteudo(self):
        for widget in self.area_conteudo.winfo_children():
            widget.destroy()

    def cabecalho_secao(self, texto):
        ctk.CTkLabel(self.area_conteudo, text=texto, font=FONTE_TITULO,
                     text_color=COR_ACCENT).pack(anchor="w", padx=30, pady=(25, 15))

    def secao_inicio(self):
        self.limpar_conteudo()
        self.cabecalho_secao(f"Bem-vindo, {self.usuario}")
        ctk.CTkLabel(
            self.area_conteudo,
            text="Use o menu à esquerda para registrar exercícios, treinos ou consultar seu histórico.",
            font=FONTE_TEXTO, text_color=COR_TEXTO_DIM,
        ).pack(anchor="w", padx=30)


    def secao_exercicios(self):
        self.limpar_conteudo()
        self.cabecalho_secao("Exercícios")

        corpo = ctk.CTkFrame(self.area_conteudo, fg_color=COR_BG_SECUNDARIO,
                              border_width=1, border_color=COR_BORDA, corner_radius=8)
        corpo.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # --- Tipo de treino: escolher existente ou criar novo ---
        ctk.CTkLabel(corpo, text="Tipo de treino", font=FONTE_SUBTITULO,
                     text_color=COR_TEXTO).pack(anchor="w", padx=20, pady=(20, 5))

        linha_tipo = ctk.CTkFrame(corpo, fg_color="transparent")
        linha_tipo.pack(fill="x", padx=20)

        tipos_existentes = list(self.exercicios_adicionados.keys()) or ["(nenhum ainda)"]
        combo_tipo = ctk.CTkOptionMenu(
            linha_tipo, values=tipos_existentes, width=220,
            fg_color=COR_BG, button_color=COR_ACCENT, button_hover_color=COR_ACCENT_HOVER,
            text_color=COR_TEXTO,
        )
        combo_tipo.pack(side="left")

        entrada_novo_tipo = ctk.CTkEntry(linha_tipo, width=180, placeholder_text="Novo tipo de treino",
                                          fg_color=COR_BG, border_color=COR_ACCENT, text_color=COR_TEXTO)
        entrada_novo_tipo.pack(side="left", padx=10)

        label_msg_tipo = ctk.CTkLabel(corpo, text="", font=FONTE_PEQUENA)
        label_msg_tipo.pack(anchor="w", padx=20)

        def criar_tipo_treino():
            novo = entrada_novo_tipo.get().strip()
            if not novo:
                self.mostrar_mensagem(label_msg_tipo, "[!] Digite um nome para o novo tipo de treino.")
                return
            if novo in self.exercicios_adicionados:
                self.mostrar_mensagem(label_msg_tipo, f"[!] '{novo}' já existe.")
                return
            self.exercicios_adicionados[novo] = []
            self.mostrar_mensagem(label_msg_tipo, f"[✔] Tipo de treino '{novo}' criado.", sucesso=True)
            entrada_novo_tipo.delete(0, "end")
            self.secao_exercicios()  # recarrega a tela com o novo tipo já disponível

        ctk.CTkButton(linha_tipo, text="+ Criar tipo", width=110, fg_color=COR_ACCENT,
                      hover_color=COR_ACCENT_HOVER, text_color=COR_BG,
                      command=criar_tipo_treino).pack(side="left")

        separador = ctk.CTkFrame(corpo, fg_color=COR_BORDA, height=1)
        separador.pack(fill="x", padx=20, pady=15)

        # --- Exercício dentro do tipo escolhido ---
        ctk.CTkLabel(corpo, text="Adicionar exercício ao tipo selecionado", font=FONTE_SUBTITULO,
                     text_color=COR_TEXTO).pack(anchor="w", padx=20, pady=(0, 5))

        linha_ex = ctk.CTkFrame(corpo, fg_color="transparent")
        linha_ex.pack(fill="x", padx=20)

        entrada_exercicio = ctk.CTkEntry(linha_ex, width=220, placeholder_text="Nome do exercício",
                                          fg_color=COR_BG, border_color=COR_ACCENT, text_color=COR_TEXTO)
        entrada_exercicio.pack(side="left")

        label_msg_ex = ctk.CTkLabel(corpo, text="", font=FONTE_PEQUENA)
        label_msg_ex.pack(anchor="w", padx=20, pady=(5, 0))

        def adicionar_exercicio():
            tipo = combo_tipo.get()
            nome = entrada_exercicio.get().strip()
            if tipo == "(nenhum ainda)":
                self.mostrar_mensagem(label_msg_ex, "[!] Crie um tipo de treino primeiro.")
                return
            if not nome:
                self.mostrar_mensagem(label_msg_ex, "[!] Digite o nome do exercício.")
                return
            if nome in self.exercicios_adicionados[tipo]:
                self.mostrar_mensagem(label_msg_ex, f"[!] '{nome}' já está cadastrado em '{tipo}'.")
                return
            self.exercicios_adicionados[tipo].append(nome)
            self.mostrar_mensagem(label_msg_ex, f"[✔] '{nome}' adicionado a '{tipo}'.", sucesso=True)
            entrada_exercicio.delete(0, "end")
            self.secao_exercicios()

        ctk.CTkButton(linha_ex, text="+ Adicionar", width=110, fg_color=COR_ACCENT,
                      hover_color=COR_ACCENT_HOVER, text_color=COR_BG,
                      command=adicionar_exercicio).pack(side="left", padx=10)

        # --- Lista de exercícios já cadastrados no tipo selecionado ---
        ctk.CTkLabel(corpo, text="Exercícios cadastrados nesse tipo:", font=FONTE_PEQUENA,
                     text_color=COR_TEXTO_DIM).pack(anchor="w", padx=20, pady=(15, 5))

        lista_scroll = ctk.CTkScrollableFrame(corpo, fg_color=COR_BG, height=120,
                                               border_width=1, border_color=COR_BORDA)
        lista_scroll.pack(fill="x", padx=20, pady=(0, 20))

        tipo_atual = combo_tipo.get()
        if tipo_atual in self.exercicios_adicionados:
            for nome_ex in self.exercicios_adicionados[tipo_atual]:
                ctk.CTkLabel(lista_scroll, text=f"• {nome_ex}", font=FONTE_TEXTO,
                             text_color=COR_TEXTO, anchor="w").pack(fill="x", padx=10, pady=2)

        combo_tipo.configure(command=lambda _: self.secao_exercicios())

    def secao_treino(self):
        self.limpar_conteudo()
        self.cabecalho_secao("Adicionar Treino")

        if not self.exercicios_adicionados:
            ctk.CTkLabel(self.area_conteudo, text="[!] Cadastre um tipo de treino e um exercício primeiro.",
                         font=FONTE_TEXTO, text_color=COR_ERRO).pack(anchor="w", padx=30)
            return

        corpo = ctk.CTkFrame(self.area_conteudo, fg_color=COR_BG_SECUNDARIO,
                              border_width=1, border_color=COR_BORDA, corner_radius=8)
        corpo.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Tipo de treino
        ctk.CTkLabel(corpo, text="Tipo de treino", font=FONTE_PEQUENA,
                     text_color=COR_TEXTO_DIM).pack(anchor="w", padx=20, pady=(20, 0))
        tipos = list(self.exercicios_adicionados.keys())
        combo_tipo = ctk.CTkOptionMenu(corpo, values=tipos, width=220,
                                        fg_color=COR_BG, button_color=COR_ACCENT,
                                        button_hover_color=COR_ACCENT_HOVER, text_color=COR_TEXTO)
        combo_tipo.pack(anchor="w", padx=20, pady=(5, 15))

        # Exercício (filtrado pelo tipo de treino)
        ctk.CTkLabel(corpo, text="Exercício", font=FONTE_PEQUENA,
                     text_color=COR_TEXTO_DIM).pack(anchor="w", padx=20)
        exercicios_do_tipo = self.exercicios_adicionados.get(combo_tipo.get(), []) or ["(nenhum cadastrado)"]
        combo_exercicio = ctk.CTkOptionMenu(corpo, values=exercicios_do_tipo, width=220,
                                             fg_color=COR_BG, button_color=COR_ACCENT,
                                             button_hover_color=COR_ACCENT_HOVER, text_color=COR_TEXTO)
        combo_exercicio.pack(anchor="w", padx=20, pady=(5, 15))

        def atualizar_exercicios(_=None):
            novos = self.exercicios_adicionados.get(combo_tipo.get(), []) or ["(nenhum cadastrado)"]
            combo_exercicio.configure(values=novos)
            combo_exercicio.set(novos[0])

        combo_tipo.configure(command=atualizar_exercicios)

        separador = ctk.CTkFrame(corpo, fg_color=COR_BORDA, height=1)
        separador.pack(fill="x", padx=20, pady=10)

        # Série atual (calculada automaticamente)
        label_serie = ctk.CTkLabel(corpo, text=f"Série nº {self.serie_atual}", font=FONTE_SUBTITULO,
                                    text_color=COR_ACCENT)
        label_serie.pack(anchor="w", padx=20, pady=(0, 10))

        linha_dados = ctk.CTkFrame(corpo, fg_color="transparent")
        linha_dados.pack(fill="x", padx=20)

        entrada_carga = ctk.CTkEntry(linha_dados, width=100, placeholder_text="Carga (Kg)",
                                      fg_color=COR_BG, border_color=COR_ACCENT, text_color=COR_TEXTO)
        entrada_carga.pack(side="left", padx=(0, 10))

        entrada_reps = ctk.CTkEntry(linha_dados, width=100, placeholder_text="Repetições",
                                     fg_color=COR_BG, border_color=COR_ACCENT, text_color=COR_TEXTO)
        entrada_reps.pack(side="left", padx=(0, 10))

        combo_rpe = ctk.CTkOptionMenu(linha_dados, values=RPE_OPCOES, width=180,
                                       fg_color=COR_BG, button_color=COR_ACCENT,
                                       button_hover_color=COR_ACCENT_HOVER, text_color=COR_TEXTO)
        combo_rpe.pack(side="left", padx=(0, 10))

        combo_obs = ctk.CTkOptionMenu(linha_dados, values=OBS_OPCOES, width=150,
                                       fg_color=COR_BG, button_color=COR_ACCENT,
                                       button_hover_color=COR_ACCENT_HOVER, text_color=COR_TEXTO)
        combo_obs.pack(side="left")

        label_msg = ctk.CTkLabel(corpo, text="", font=FONTE_PEQUENA)
        label_msg.pack(anchor="w", padx=20, pady=(15, 0))

        def salvar_serie():
            tipo = combo_tipo.get()
            exercicio = combo_exercicio.get()
            if exercicio == "(nenhum cadastrado)":
                self.mostrar_mensagem(label_msg, "[!] Não há exercícios cadastrados nesse tipo de treino.")
                return
            try:
                carga = float(entrada_carga.get().replace(",", "."))
                reps = int(entrada_reps.get())
            except ValueError:
                self.mostrar_mensagem(label_msg, "[!] Carga e repetições precisam ser números válidos.")
                return

            self.exercicios_adicionados.setdefault(tipo, [])
            self.treinos_adicionados.setdefault(tipo, {})
            self.treinos_adicionados[tipo].setdefault(exercicio, [])

            data_hoje = dt.datetime.now().strftime("%d-%m-%y")

            # Reaproveita a sessão de hoje se já foi criada (mesma lógica do terminal:
            # não sobrescreve, só cria na primeira série da sessão)
            if self.sessao_treino_ativa is None:
                nova_sessao = {"data": data_hoje, "series": []}
                self.treinos_adicionados[tipo][exercicio].append(nova_sessao)
                self.sessao_treino_ativa = nova_sessao

            self.sessao_treino_ativa["series"].append({
                "serie": self.serie_atual, "carga": carga, "reps": reps,
                "rpe": combo_rpe.get(), "obs": combo_obs.get(),
            })

            self.mostrar_mensagem(label_msg, f"[✔] Série {self.serie_atual} salva com sucesso.", sucesso=True)

            # Reseta apenas carga/reps/rpe/obs — tipo/exercício continuam selecionados
            entrada_carga.delete(0, "end")
            entrada_reps.delete(0, "end")
            combo_rpe.set(RPE_OPCOES[0])
            combo_obs.set(OBS_OPCOES[0])
            self.serie_atual += 1
            label_serie.configure(text=f"Série nº {self.serie_atual}")

        ctk.CTkButton(corpo, text="Salvar Série", font=FONTE_TEXTO, width=160,
                      fg_color=COR_ACCENT, hover_color=COR_ACCENT_HOVER, text_color=COR_BG,
                      command=salvar_serie).pack(anchor="w", padx=20, pady=20)

        def novo_exercicio():
            self.serie_atual = 1
            self.sessao_treino_ativa = None
            self.secao_treino()

        ctk.CTkButton(corpo, text="Novo exercício / nova sessão", font=FONTE_PEQUENA, width=220,
                      fg_color="transparent", hover_color=COR_BG, border_width=1,
                      border_color=COR_ACCENT, text_color=COR_ACCENT,
                      command=novo_exercicio).pack(anchor="w", padx=20, pady=(0, 20))

    def secao_consulta(self):
        self.limpar_conteudo()
        self.cabecalho_secao("Consulta")

        abas = ctk.CTkTabview(
            self.area_conteudo, fg_color=COR_BG_SECUNDARIO,
            segmented_button_selected_color=COR_ACCENT,
            segmented_button_selected_hover_color=COR_ACCENT_HOVER,
            segmented_button_unselected_color=COR_BG,
            text_color=COR_TEXTO, border_width=1, border_color=COR_BORDA,
        )
        abas.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        aba_tipos = abas.add("Tipos de Treino")
        aba_exercicios = abas.add("Exercícios")
        aba_treinos = abas.add("Treinos")

        self._preencher_aba_tipos(aba_tipos)
        self._preencher_aba_exercicios(aba_exercicios)
        self._preencher_aba_treinos(aba_treinos)

    def _preencher_aba_tipos(self, aba):
        if not self.exercicios_adicionados:
            ctk.CTkLabel(aba, text="Nenhum tipo de treino cadastrado ainda.",
                         font=FONTE_TEXTO, text_color=COR_TEXTO_DIM).pack(padx=15, pady=15, anchor="w")
            return
        for tipo in list(self.exercicios_adicionados.keys()):
            linha = ctk.CTkFrame(aba, fg_color="transparent")
            linha.pack(fill="x", padx=15, pady=4)
            ctk.CTkLabel(linha, text=tipo, font=FONTE_TEXTO, text_color=COR_TEXTO).pack(side="left")

            def remover(t=tipo):
                del self.exercicios_adicionados[t]
                self.treinos_adicionados.pop(t, None)
                self.secao_consulta()

            ctk.CTkButton(linha, text="Remover", width=90, fg_color="transparent",
                          border_width=1, border_color=COR_ERRO, text_color=COR_ERRO,
                          hover_color=COR_BG, command=remover).pack(side="right")

    def _preencher_aba_exercicios(self, aba):
        if not self.exercicios_adicionados:
            ctk.CTkLabel(aba, text="Nenhum exercício cadastrado ainda.",
                         font=FONTE_TEXTO, text_color=COR_TEXTO_DIM).pack(padx=15, pady=15, anchor="w")
            return
        for tipo, lista_exercicios in self.exercicios_adicionados.items():
            if not lista_exercicios:
                continue
            ctk.CTkLabel(aba, text=tipo, font=FONTE_SUBTITULO,
                         text_color=COR_ACCENT).pack(anchor="w", padx=15, pady=(10, 2))
            for exercicio in list(lista_exercicios):
                linha = ctk.CTkFrame(aba, fg_color="transparent")
                linha.pack(fill="x", padx=25, pady=2)
                ctk.CTkLabel(linha, text=exercicio, font=FONTE_TEXTO,
                             text_color=COR_TEXTO).pack(side="left")

                def remover(t=tipo, e=exercicio):
                    self.exercicios_adicionados[t].remove(e)
                    if not self.exercicios_adicionados[t]:
                        del self.exercicios_adicionados[t]
                    self.secao_consulta()

                ctk.CTkButton(linha, text="Remover", width=90, fg_color="transparent",
                              border_width=1, border_color=COR_ERRO, text_color=COR_ERRO,
                              hover_color=COR_BG, command=remover).pack(side="right")

    def _preencher_aba_treinos(self, aba):
        tem_treino = any(self.treinos_adicionados.get(t, {}) for t in self.treinos_adicionados)
        if not tem_treino:
            ctk.CTkLabel(aba, text="Nenhum treino registrado ainda.",
                         font=FONTE_TEXTO, text_color=COR_TEXTO_DIM).pack(padx=15, pady=15, anchor="w")
            return

        for tipo in self.treinos_adicionados:
            for exercicio, sessoes in self.treinos_adicionados[tipo].items():
                if not sessoes:
                    continue
                ctk.CTkLabel(aba, text=f"{tipo} — {exercicio}", font=FONTE_SUBTITULO,
                             text_color=COR_ACCENT).pack(anchor="w", padx=15, pady=(10, 2))
                for sessao in list(sessoes):
                    linha = ctk.CTkFrame(aba, fg_color=COR_BG, border_width=1, border_color=COR_BORDA)
                    linha.pack(fill="x", padx=25, pady=3)
                    texto = f"Data: {sessao['data']}  |  {len(sessao['series'])} série(s)"
                    ctk.CTkLabel(linha, text=texto, font=FONTE_TEXTO,
                                 text_color=COR_TEXTO).pack(side="left", padx=10, pady=6)

                    def remover(t=tipo, e=exercicio, s=sessao):
                        self.treinos_adicionados[t][e].remove(s)
                        if not self.treinos_adicionados[t][e]:
                            del self.treinos_adicionados[t][e]
                        self.secao_consulta()

                    ctk.CTkButton(linha, text="Remover", width=90, fg_color="transparent",
                                  border_width=1, border_color=COR_ERRO, text_color=COR_ERRO,
                                  hover_color=COR_BG, command=remover).pack(side="right", padx=10)


    def secao_estatistica(self):
        self.limpar_conteudo()
        self.cabecalho_secao("Estatística")
        ctk.CTkLabel(
            self.area_conteudo,
            text="[Em construção] Aqui vai entrar a evolução de carga/RPE por exercício ao longo do tempo.",
            font=FONTE_TEXTO, text_color=COR_TEXTO_DIM,
        ).pack(anchor="w", padx=30)


    def secao_ajuda(self):
        self.limpar_conteudo()
        self.cabecalho_secao("Ajuda")
        texto = (
            "1. Vá em 'Exercícios' pra cadastrar seus tipos de treino e exercícios.\n"
            "2. Vá em 'Treino' pra registrar as séries do dia, escolhendo entre o que já foi cadastrado.\n"
            "3. Vá em 'Consulta' pra ver e remover o que já foi cadastrado/registrado.\n"
            "4. Seus dados são salvos automaticamente ao sair do programa."
        )
        ctk.CTkLabel(self.area_conteudo, text=texto, font=FONTE_TEXTO,
                     text_color=COR_TEXTO, justify="left").pack(anchor="w", padx=30)


    def sair(self):
        if self.usuario:
            salvar_tudo(self.usuario, self.treinos_adicionados, self.exercicios_adicionados)
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()