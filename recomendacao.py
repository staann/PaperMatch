import pandas as pd
import numpy as np

# --- Carregando todos os componentes necessários para a função ---

# 1. O DataFrame de artigos (certifique-se de que ele está carregado)
df_artigos = pd.read_csv('dados_tratados.csv') 

# 2. O DataFrame de avaliações (o que você acabou de gerar)
df_avaliacoes = pd.read_csv('avaliacoes_simuladas.csv')

# 3. A matriz de similaridade (que você calculou e salvou)
cosine_sim_matrix = np.load('cosine_similarity_matrix.npy')

# 4. Um mapeamento do ID do artigo para o índice da linha no DataFrame
# Isso é um truque de performance para encontrar rapidamente a posição de um artigo na matriz
indices = pd.Series(df_artigos.index, index=df_artigos['ids']).drop_duplicates()


# --- A FUNÇÃO PRINCIPAL DE RECOMENDAÇÃO ---

def obter_recomendacoes(user_id, top_n=10):
    """
    Gera uma lista de recomendações para um usuário específico,
    baseado no conteúdo dos artigos que ele já avaliou positivamente. [cite: 9]
    """
    
    # 1. Encontrar todos os artigos que o usuário avaliou
    avaliacoes_do_usuario = df_avaliacoes[df_avaliacoes['user_id'] == user_id]
    
    # 2. Filtrar para pegar apenas os artigos que o usuário gostou (nota >= 4)
    artigos_que_gostou = avaliacoes_do_usuario[avaliacoes_do_usuario['rating'] >= 4]
    
    if artigos_que_gostou.empty:
        return ["Não há avaliações positivas suficientes para gerar recomendações."]

    # 3. Para cada artigo que o usuário gostou, acumular os scores de similaridade
    scores_agregados = {}
    for index, row in artigos_que_gostou.iterrows():
        artigo_id = row['artigo_id']
        nota = row['rating']
        
        # Pega o índice do artigo na matriz de similaridade
        idx_artigo = indices[artigo_id]
        
        # Pega a linha de scores de similaridade para este artigo
        # e pondera pela nota (um item nota 5 tem mais influência)
        vetor_similaridade = cosine_sim_matrix[idx_artigo] * nota

        # Soma os scores ponderados no nosso dicionário agregado
        for idx_similar, score in enumerate(vetor_similaridade):
            scores_agregados[idx_similar] = scores_agregados.get(idx_similar, 0) + score

    # 4. Remover artigos que o usuário já avaliou da lista de candidatos
    indices_ja_avaliados = [indices[artigo_id] for artigo_id in avaliacoes_do_usuario['artigo_id']]
    for idx in indices_ja_avaliados:
        if idx in scores_agregados:
            del scores_agregados[idx]

    # 5. Ordenar os artigos restantes pelo score agregado e pegar os 'top_n' melhores
    indices_recomendados = sorted(scores_agregados, key=scores_agregados.get, reverse=True)[:top_n]
    
    # 6. Retornar os títulos dos artigos recomendados
    return df_artigos.iloc[indices_recomendados]['titles'].tolist()


# --- TESTANDO A FUNÇÃO ---
print("Função 'obter_recomendacoes' definida. Vamos testá-la...")

# Pega o primeiro ID de usuário único do nosso dataset de avaliações para o teste
id_usuario_teste = df_avaliacoes['user_id'].unique()[0]

print(f"\\n--- TESTE PARA O USUÁRIO: {id_usuario_teste} ---")

# Mostra o que esse usuário gostou para podermos validar a recomendação
avaliacoes_positivas_teste = df_avaliacoes[(df_avaliacoes['user_id'] == id_usuario_teste) & (df_avaliacoes['rating'] >= 4)]
titulos_gostou = df_artigos[df_artigos['ids'].isin(avaliacoes_positivas_teste['artigo_id'])]['titles'].tolist()

print("\\nEste usuário gostou de:")
for titulo in titulos_gostou:
    print(f"- {titulo}")

# Chama a função para gerar as recomendações
recomendacoes = obter_recomendacoes(user_id=id_usuario_teste, top_n=5)

print("\\nRecomendações geradas pelo sistema:")
for i, rec_titulo in enumerate(recomendacoes):
    print(f"{i+1}. {rec_titulo}")



# --- Bibliotecas necessárias para a interface ---
import ipywidgets as widgets
from IPython.display import display, clear_output
import pandas as pd

# --- WIDGETS DA INTERFACE ---

# Etapa 1: Caixa de texto para o nome do novo usuário
input_usuario = widgets.Text(
    placeholder='Digite seu nome aqui...',
    description='Novo Usuário:',
    disabled=False
)

# Etapa 1: Botão para iniciar o processo
botao_cadastrar = widgets.Button(
    description='Criar Perfil',
    button_style='success', # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Clique para iniciar a avaliação de artigos e criar seu perfil.',
    icon='user-plus'
)

# Container para os widgets de avaliação que serão criados dinamicamente
box_perfil_avaliacoes = widgets.VBox([])

# Container para a saída final das recomendações
output_final = widgets.Output()


# --- LÓGICA DA INTERFACE ---

def iniciar_criacao_perfil(b):
    """
    Esta função é chamada quando o botão 'Criar Perfil' é clicado.
    Ela monta a tela de avaliação de artigos.
    """
    # Pega o nome do usuário digitado
    nome_usuario = input_usuario.value
    if not nome_usuario:
        print("Por favor, digite um nome de usuário antes de continuar.")
        return

    # Limpa a tela anterior
    clear_output(wait=True)
    
    # Seleciona 5 artigos aleatórios para o usuário avaliar
    artigos_para_avaliar = df_artigos.sample(5)
    
    # Cria os componentes da tela de avaliação
    label_perfil = widgets.Label("Para entendermos seu gosto, avalie os seguintes artigos de 1 a 5:")
    
    # Cria um slider para cada artigo a ser avaliado
    sliders = []
    for _, row in artigos_para_avaliar.iterrows():
        slider = widgets.IntSlider(
            min=1, max=5, value=3, # Começa com nota 3 (neutra)
            description=row['titles'], 
            style={'description_width': 'initial'} # Evita que o título seja cortado
        )
        # Anexa o ID do artigo ao widget para uso posterior
        slider.artigo_id = row['ids'] 
        sliders.append(slider)
        
    botao_recomendar = widgets.Button(description='Gerar Recomendações', button_style='info', icon='lightbulb')
    
    # Define o que acontece quando o botão 'Gerar Recomendações' é clicado
    def obter_recomendacoes_novo_usuario(b):
        # Limpa a tela de avaliação
        clear_output(wait=True)
        # Mostra a área de saída final
        display(output_final)
        
        with output_final:
            print(f"Olá, {nome_usuario}! Com base no seu perfil, aqui estão suas recomendações:")
            
            # Coleta as avaliações dos sliders
            novas_avaliacoes = [{'user_id': nome_usuario, 'artigo_id': s.artigo_id, 'rating': s.value} for s in sliders]
            novas_avaliacoes_df = pd.DataFrame(novas_avaliacoes)
            
            # Adiciona as novas avaliações ao DataFrame global de avaliações
            global df_avaliacoes
            df_avaliacoes = pd.concat([df_avaliacoes, novas_avaliacoes_df], ignore_index=True)
            
            # Chama a sua função principal para obter as recomendações
            recomendacoes = obter_recomendacoes(user_id=nome_usuario, top_n=5)
            
            # Exibe as recomendações de forma legível
            print("-" * 50)
            for i, titulo in enumerate(recomendacoes):
                print(f"{i+1}. {titulo}")
            print("-" * 50)

    botao_recomendar.on_click(obter_recomendacoes_novo_usuario)
    
    # Monta e exibe a tela de avaliação
    box_perfil_avaliacoes.children = [label_perfil] + sliders + [botao_recomendar]
    display(box_perfil_avaliacoes)

# Conecta a função ao clique do botão de cadastro inicial
botao_cadastrar.on_click(iniciar_criacao_perfil)


# --- EXIBIÇÃO INICIAL ---
# Exibe a primeira tela para o usuário (cadastro)
display(input_usuario, botao_cadastrar)