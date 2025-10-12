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