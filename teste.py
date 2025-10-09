import pandas as pd
import numpy as np
import random

# --- PREPARAÇÃO (mesmo de antes) ---
# Usando o mesmo DataFrame de artigos simulado.
categorias_disponiveis = ['cs.AI', 'cs.LG', 'cs.CV', 'math.ST', 'physics.optics', 'cs.DB']
dados_simulados = {
    'artigo_id': range(1, 41), # Aumentando para ter mais variedade
    'titulo': [f'Título do Artigo {i}' for i in range(1, 41)],
    'categories': [random.choice(categorias_disponiveis) for _ in range(40)]
}
artigos_df = pd.DataFrame(dados_simulados)

# --- PASSO 1: CRIAR PERFIS PONDERADOS E COMPLEXOS ---

num_usuarios = 100
perfis_usuarios_ponderados = {}
lista_de_categorias = artigos_df['categories'].unique()

for user_id in range(1, num_usuarios + 1):
    # Cada usuário terá de 1 a 3 interesses
    num_interesses = np.random.randint(1, 4)
    
    # Sorteia as categorias de interesse do usuário, sem repetição
    interesses = np.random.choice(lista_de_categorias, num_interesses, replace=False)
    
    # Gera pesos aleatórios para cada interesse
    pesos = np.random.rand(num_interesses)
    # Normaliza os pesos para que a soma seja 1 (ex: [0.3, 0.8] -> [0.27, 0.73])
    pesos_normalizados = pesos / np.sum(pesos)
    
    # Cria o perfil ponderado
    # Ex: {'cs.AI': 0.65, 'cs.CV': 0.35}
    perfis_usuarios_ponderados[user_id] = dict(zip(interesses, pesos_normalizados))

print("--- Exemplo de Perfis Ponderados Criados ---")
for i in range(1, 4):
    print(f"Usuário {i}: {perfis_usuarios_ponderados[i]}")
print("\n")

# --- PASSO 2: GERAR AVALIAÇÕES BASEADAS NOS PERFIS PONDERADOS ---

num_avaliacoes = 500
lista_avaliacoes = []

for _ in range(num_avaliacoes):
    usuario_atual_id = np.random.randint(1, num_usuarios + 1)
    perfil_usuario = perfis_usuarios_ponderados[usuario_atual_id]
    
    interesses_usuario = list(perfil_usuario.keys())
    probabilidades = list(perfil_usuario.values())
    
    # 85% de chance de avaliar um artigo DENTRO dos seus interesses
    if np.random.rand() < 0.85:
        # Escolhe uma das categorias de interesse, respeitando a probabilidade/peso
        categoria_escolhida = np.random.choice(interesses_usuario, p=probabilidades)
        
        # Define a nota com base na força do interesse (peso)
        peso_do_interesse = perfil_usuario[categoria_escolhida]
        if peso_do_interesse > 0.5: # Interesse Principal
            nota = 5
        elif peso_do_interesse > 0.2: # Interesse Secundário
            nota = np.random.choice([4, 5])
        else: # Interesse Terciário
            nota = np.random.choice([3, 4])
            
        artigos_para_escolha = artigos_df[artigos_df['categories'] == categoria_escolhida]

    # 15% de chance de "explorar" um tema aleatório
    else:
        # Atribui uma nota mais baixa para exploração
        nota = np.random.choice([1, 2, 3])
        # Garante que o artigo escolhido não seja de um dos interesses principais
        artigos_para_escolha = artigos_df[~artigos_df['categories'].isin(interesses_usuario)]

    # Se a filtragem resultar em uma lista vazia, pega qualquer artigo
    if artigos_para_escolha.empty:
        artigos_para_escolha = artigos_df

    artigo_escolhido = artigos_para_escolha.sample(1)
    artigo_id = artigo_escolhido['artigo_id'].iloc[0]
    
    lista_avaliacoes.append({
        'user_id': usuario_atual_id,
        'artigo_id': artigo_id,
        'rating': nota
    })

# --- FINALIZAÇÃO ---
matriz_utilidade_df = pd.DataFrame(lista_avaliacoes).drop_duplicates(subset=['user_id', 'artigo_id'], keep='last')

print("--- Matriz de Utilidade Gerada com Perfis Ponderados ---")
print(matriz_utilidade_df.head(10))

print("\n--- Verificando Avaliações de um Usuário com Múltiplos Interesses ---")
# Filtra um usuário para ver se ele deu notas altas para artigos de categorias diferentes
# (O resultado pode variar a cada execução)
try:
    user_id_exemplo = 2 # Vamos analisar o usuário 2
    avaliacoes_exemplo = matriz_utilidade_df[matriz_utilidade_df['user_id'] == user_id_exemplo]
    # Junta com os dados dos artigos para ver as categorias
    avaliacoes_exemplo_com_categoria = pd.merge(avaliacoes_exemplo, artigos_df, on='artigo_id')
    print(f"Interesses do Usuário {user_id_exemplo}: {perfis_usuarios_ponderados[user_id_exemplo]}")
    print(avaliacoes_exemplo_com_categoria[['user_id', 'artigo_id', 'rating', 'categories']])
except KeyError:
    print(f"Usuário {user_id_exemplo} não apareceu nas amostras. Tente rodar novamente.")