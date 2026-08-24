import utils as ut
agrupamento_musculares = ["Peito","Costa","Quadriceps","Posterior","Biceps","Triceps","Abdomen","Antebraço","Panturrilha","Gluteo"]
def adicionar_exercicio(exercicios_adicionados):
    print("\n=== [ Adicionar Exercício ] ===")
    tipo_treino = str(input("Digite a divisão/tipo de treino: "))
    
    if tipo_treino not in exercicios_adicionados.keys():
        exercicios_adicionados[tipo_treino] = []
    while True:
        nome_exercicio = str(input("Nome do exercício: "))
        if nome_exercicio in exercicios_adicionados[tipo_treino]:
            print(f"\n[!] O exercício '{nome_exercicio}' já está cadastrado neste treino.")
            print(f"[!] Por favor, digite um nome diferente.")
        else:
            break
    exercicios_adicionados[tipo_treino].append(nome_exercicio)
    print(f"\n[✔] '{nome_exercicio}' adicionado ao treino '{tipo_treino}'.")
    return exercicios_adicionados

def listar_exercicios_especifico(exercicios_adicionados, tipo_treino):
    print(f"\n=== [ Exercícios no treino '{tipo_treino}' ] ===")
    print(" | ".join(exercicios_adicionados[tipo_treino]))

def listar_exercicios_completo(exercicios_adicionados):   
    print("\n=== [ Todos os Exercícios Cadastrados ] ===")
    for tipo_treino, lista_exercicios in exercicios_adicionados.items():
        exercicios_texto = ", ".join(lista_exercicios)
        print(f"-> Treino: {tipo_treino} | Exercícios: {exercicios_texto}")

def listar_tipos_treino(exercicios_adicionados):
    print("\n=== [ Tipos de Treino Cadastrados ] ===")
    print(" | ".join(exercicios_adicionados.keys()))

def alterar_exercicio(exercicios_adicionados):
    print("\n=== [ Alterar Exercício ] ===")
    while True:
        listar_tipos_treino(exercicios_adicionados)
        tipo_treino = str(input("\nDigite o treino do exercício que deseja alterar: "))
        if tipo_treino not in exercicios_adicionados.keys():
            print(f"\n[!] O treino '{tipo_treino}' não existe.")
            print(f"[!] Escolha uma opção válida da lista.")
        else:
            while True:
                nome_exercicio_alterado = str(input("Nome do exercício que será substituído: "))
                if nome_exercicio_alterado not in exercicios_adicionados[tipo_treino]:
                    print(f"\n[!] '{nome_exercicio_alterado}' não encontrado no treino '{tipo_treino}'.")
                    listar_exercicios_especifico(exercicios_adicionados, tipo_treino)
                else:
                    novo_nome = str(input(f"Digite o novo nome para '{nome_exercicio_alterado}': "))
                    exercicios_adicionados[tipo_treino].remove(nome_exercicio_alterado)
                    exercicios_adicionados[tipo_treino].append(novo_nome)
                    print(f"\n[✔] '{nome_exercicio_alterado}' alterado para '{novo_nome}'.")
                    break
            break
    return exercicios_adicionados  

def remover_exercicio(exercicios_adicionados):
    print("\n=== [ Remover Exercício ] ===")
    while True:
        listar_exercicios_completo(exercicios_adicionados)
        tipo_treino = str(input("\nDigite o treino do exercício que deseja remover: "))            
        if tipo_treino not in exercicios_adicionados.keys():
            print(f"\n[!] O treino '{tipo_treino}' não existe.")
        else:
            while True:
                nome_exercicio_removido = str(input("Nome do exercício a ser removido: "))
                if nome_exercicio_removido not in exercicios_adicionados[tipo_treino]:
                        print(f"\n[!] '{nome_exercicio_removido}' não encontrado no treino '{tipo_treino}'.")
                        listar_exercicios_especifico(exercicios_adicionados, tipo_treino)
                else:
                    exercicios_adicionados[tipo_treino].remove(nome_exercicio_removido)
                    print(f"\n[✔] Exercício '{nome_exercicio_removido}' removido do treino '{tipo_treino}'.")
                    if not exercicios_adicionados[tipo_treino]:
                        del exercicios_adicionados[tipo_treino]
                        print(f"[✔] O treino '{tipo_treino}' ficou vazio e foi removido.")
                    break
            break
    return exercicios_adicionados