"""NOT USED"""

from timeit import default_timer as timer

import random
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from objects.db_objects.games import Games
from objects.db_objects.games_categories import GamesCategories
from objects.db_objects.category import Category

from app import db

start = timer()

# def content_recommendations
df = pd.read_sql(
    db.session.query(
        Games.title, Games.developer, Games.publisher, Category.tag, GamesCategories
    )
    .filter(GamesCategories.game_id == Games._id)
    .filter(GamesCategories.category_id == Category._id)
    .statement,
    db.session.bind,
)


# important columns for recommending
columns = ["title", "developer", "publisher", "tag"]


def combine_features(data):
    features = []
    for i in range(0, data.shape[0]):
        features.append(
            data["title"][i]
            + " "
            + data["developer"][i]
            + " "
            + data["publisher"][i]
            + " "
            + data["tag"][i]
        )
    # print(features)
    return features


df["combined_features"] = combine_features(df)
# combining new column text into matrix of word counts?
cm = CountVectorizer().fit_transform(df["combined_features"])
# get cosine similarity matrix from count matrix
cs = cosine_similarity(cm)
# print similarity of each game. 1 = same game

# get title of game a player likes
# title = df['title'][random.randint(1, 49)]
title = df["title"][31]
print(title)
# TODO possible site implementation: this is the line the game_recommender bases suggestion on
#  can implement as a random selection of any game a user has rated above a 7,
#  and pass that for a given instance of a home-page loading

# checking the dataframe instead of checking the database
game_id = df[df.title == title]["id"].values[0]
# create list of tuples form (game_id, similarity score)
scores = list(enumerate(cs[game_id]))
# sort score descending, and show all but the highest as this will be self
sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:]

# loop thru top 3 recommendations
j = 0
print(f"Top 3 Game Recommendations based on {title} are: ")
for item in sorted_scores:
    game_title = df[df.id == item[0]]["title"].values
    print(j + 1, game_title[0])
    j = j + 1
    if j >= 3:
        break

end = timer()

print(end - start)
