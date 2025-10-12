import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
# --- Carregando seus dados ---
try:
    df_artigos = pd.read_csv('dados_tratados.csv')
    
    # Tratamento de possíveis valores nulos nos textos
    df_artigos['titles'] = df_artigos['titles'].fillna('')
    df_artigos['abstracts'] = df_artigos['abstracts'].fillna('')

    # --- PASSO 1: Preparar o Conteúdo ---
    # Vamos combinar o título e o resumo em um único campo de texto ("documento")
    # para que o TF-IDF possa analisá-los juntos.
    df_artigos['conteudo_completo'] = df_artigos['titles'] + ' ' + df_artigos['abstracts']
    print("Coluna 'conteudo_completo' criada com sucesso.")

    # --- PASSO 2: Vetorização com TF-IDF ---
    print("Iniciando a vetorização com TF-IDF...")
    
    # Inicializa o vetorizador. 
    # stop_words='english' remove palavras comuns em inglês (como 'the', 'a', 'is')
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')

    # 'fit_transform' aprende o vocabulário e transforma o texto em uma matriz numérica
    tfidf_matrix = tfidf_vectorizer.fit_transform(df_artigos['conteudo_completo'])
    
    print("Matriz TF-IDF criada com sucesso!")
    print(f"Dimensões da matriz: {tfidf_matrix.shape}") # (nº de artigos, nº de palavras únicas)

    # --- PASSO 3: Cálculo da Similaridade de Cosseno ---
    print("\nCalculando a matriz de similaridade de cosseno...")
    
    cosine_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    print("Matriz de similaridade calculada com sucesso!")
    print(f"Dimensões da matriz de similaridade: {cosine_sim_matrix.shape}")

    # Agora a 'cosine_sim_matrix' está pronta para ser usada pela sua função de recomendação!
    # Por exemplo, cosine_sim_matrix[0][1] te dará a similaridade entre o primeiro e o segundo artigo.

    # --- SALVANDO A MATRIZ ---
    print("\nSalvando a matriz de similaridade em um arquivo...")

    # np.save('nome_do_arquivo.npy', sua_matriz)
    np.save('cosine_similarity_matrix.npy', cosine_sim_matrix)

    print("Matriz salva com sucesso como 'cosine_similarity_matrix.npy'")

except FileNotFoundError:
    print("Erro: O arquivo 'dados_tratados.csv' não foi encontrado.")