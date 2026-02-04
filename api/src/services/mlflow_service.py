import pickle
import mlflow
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src.models.recipe import get_recipes


# recommandations selon le modèle MLFlow
def get_recommendations():
    mlflow.set_tracking_uri("http://mlflow:5000")
    dep = mlflow.pyfunc.get_model_dependencies("models:/Recommendation_model/Production")
    print("dep")
    model = mlflow.pyfunc.load_model(
        "models:/Recommendation_model/Production"
    )

    recettes = get_recipes()
    print(recettes)
    df_recettes = pd.DataFrame(recettes, columns=["id", "nom", "like"])

    recommendations = model.predict(df_recettes)
    print(recommendations)
    return recommendations