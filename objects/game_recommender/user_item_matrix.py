import pandas as pd

from objects.db_objects.recommended_games import RecommendedGames
from objects.db_objects.users import Users
from objects.db_objects.users_games import UsersGames
from objects.db_objects.posts import Posts
from objects.db_objects.games import Games
from objects.db_objects.comments import Comments
from objects.db_objects.category import Category
from objects.db_objects.games_categories import GamesCategories

from app import db


def matrix_gen():
    data = pd.read_sql(
        db.session.query(UsersGames.game_id, UsersGames.user_id, UsersGames.score)
        .filter(UsersGames.game_id == Games._id)
        .filter(UsersGames.user_id == Users._id)
        .statement,
        db.session.bind,
    )

    # print(data)

    data = data[data.score.notnull()]
    data["score"] = data["score"].astype(int)
    # print(data)

    matrix = data.pivot(index="user_id", columns="game_id", values="score")
    return matrix
    # matrix = data.pivot(index='user_id', columns='game_id', values='score').fillna(0)

    # TODO check that null entries are not being processed as ZEROS
    #  if they are, less popular game scores would result in lower averages due to more zeros.
    #  either return nulls, or check effect of returning ZEROS as five to push average
    # FIXME do i need to leave empty spots as NaNs? and not 0?

# print(matrix)

# print(len(matrix.columns))


# if __name__ == "__main__":
#     factorizer()
