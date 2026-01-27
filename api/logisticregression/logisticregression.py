from sklearn.model_selection import train_test_split
from sklearn import datasets, linear_model, metrics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
import pandas as pd


# Load dataset
#à écrire le code quand la bdd sera dispo


#use TF-IDF to vectorize the text data (ingredients) TF-IDF is a method using text frequency and inverse document frequency to assign weights to words based on their importance in a document relative to a collection of documents. to convert into number
# tfidf = TfidfVectorizer(
#     ngram_range=(1,2),
#     min_df=5,
#     max_df=0.9
# )

# #combine preprocessing steps using ColumnTransformer for different feature types
# #à adapter en fonction des features dispo dans la bdd
# preprocess = ColumnTransformer(
#     transformers=[
#         ("text", tfidf, "ingredients"),
#         ("num", StandardScaler(), ["temps", "calories"])
#     ]
# )

# model = Pipeline(
#     steps=[
#         ("prep", preprocess),
#         ("clf", LogisticRegression(max_iter=1000))
#     ]
# )


#split data into training and testing sets
#y = df["liked"].astype(int)
#model.fit(X=df, y=y)




#y_pred = model.predict()

#print(f"Logistic Regression model accuracy: {metrics.accuracy_score(y_test, y_pred) * 100:.2f}%")