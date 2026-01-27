import pandas as pd
from api.src.models.recipe import get_recipes
import numpy as np
import scipy.sparse as sparse
import implicit
import pickle
import mlflow

# Préparation des données
# Tables de toutes les recettes
#recettes = get_recipes()
recettes = [(1, "Gâteau Chocolat", 500), (2, "Tarte aux Pommes", 120), (3, "Poulet Curry", 900)]
utilisateurs = [{'id': 10, 'nom': 'Alice', 'likes': [1, 2]}, {'id': 20, 'nom': 'Bob', 'likes': [3]}]
df_recettes = pd.DataFrame(recettes, columns=['id', 'nom', 'likes'])

#utilisateurs = get_utilisateurs()


# On a besoin de mapper les ID SQL vers des index (0, 1, 2...)
# C'est nous qui le faisons manuellement car implicit n'a pas de classe "Dataset"
user_ids = [u['id'] for u in utilisateurs]
item_ids = df_recettes['id'].tolist()

# Dictionnaires de mapping
user_map = {id_sql: idx for idx, id_sql in enumerate(user_ids)}
item_map = {id_sql: idx for idx, id_sql in enumerate(item_ids)}
# Inverses pour récupérer les IDs à la fin
inv_user_map = {v: k for k, v in user_map.items()}
inv_item_map = {v: k for k, v in item_map.items()}

# Création des listes pour la matrice sparse
row_ind = [] # Items
col_ind = [] # Users
data = []    # 1 (le like)

for u in utilisateurs:
    u_idx = user_map[u['id']]
    for r_id in u['likes']:
        if r_id in item_map: # Sécurité
            r_idx = item_map[r_id]
            # ATTENTION : Implicit veut ITEM en ligne, USER en colonne
            row_ind.append(r_idx)
            col_ind.append(u_idx)
            data.append(1) # Valeur du like

# Création de la matrice sparse CSR
# Dimension : (Nb_Items, Nb_Users)
interaction_matrix = sparse.csr_matrix((data, (row_ind, col_ind)), shape=(len(item_ids), len(user_ids)))

# --- 2. ENTRAÎNEMENT AVEC MLFLOW ---
mlflow.set_experiment("Reco_Implicit_ALS")

with mlflow.start_run():
    # Paramètres du modèle ALS (Alternating Least Squares)
    factors = 50
    iterations = 15
    regularization = 0.01
    
    mlflow.log_params({"factors": factors, "iterations": iterations})

    # Initialisation du modèle
    model = implicit.als.AlternatingLeastSquares(
        factors=factors, 
        regularization=regularization, 
        iterations=iterations,
        random_state=42
    )

    # Entraînement (Le modèle attend la matrice Item-User)
    print("Entraînement...")
    model.fit(interaction_matrix)

    # Sauvegarde
    with open('implicit_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    mlflow.log_artifact('implicit_model.pkl')
    print("Modèle sauvegardé.")

# --- 3. FONCTION DE RECOMMANDATION ---
def recommend_implicit(user_id_sql, model, interaction_matrix, user_map, inv_item_map, N=5):
    if user_id_sql not in user_map:
        return [] # Cold Start (Utilisateur inconnu)
    
    user_idx = user_map[user_id_sql]
    
    # Implicit a besoin de la matrice transposée (User-Item) pour filtrer ce qui est déjà vu
    user_items = interaction_matrix.T.tocsr()
    
    # La fonction magique recommend()
    # Elle renvoie (item_idx, score)
    ids, scores = model.recommend(user_idx, user_items[user_idx], N=N)
    
    # Conversion Index -> ID SQL
    recos_sql = [inv_item_map[idx] for idx in ids]
    return recos_sql

# TEST
print("Reco pour user 10:", recommend_implicit(10, model, interaction_matrix, user_map, inv_item_map))