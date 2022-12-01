import random
import pandas as pd
from app import db
from objects.db_objects.games import Games
from objects.db_objects.users_games import UsersGames

# needed for relationships, even while not explicitly used
from objects.db_objects.games_categories import GamesCategories
from objects.db_objects.category import Category

""" grab one game on a user list with a rating of 8 or higher, each time they hit HOME"""


def recommend(user_id):
    # TODO make a number list (by length of users.query.all()? )
    #  then pop each item as selected in random_liked_game
    #  to ensure process is not re-checking the same failed number multiple times

    # TODO solution where user does not like popular games / has no games fitting required criteria?

    should_restart = True
    runs = 0
    user_list_len = 0
    # can maybe use liked_games length for this
    liked_games = []

    """ make sure the randomly selected game is liked by more than zero other users"""
    while should_restart is True:
        runs += 1
        if runs == 10:
            # TODO replace this breaker with breaker based on length of user game list
            break
        users_games = UsersGames.query.filter_by(user_id=user_id).all()
        for game in users_games:
            try:
                if int(game.score) >= 8:
                    liked_games.append(game.game_id)
            except TypeError as e:
                pass
        # select random game from user list if score is above 8
        random_liked_game = random.choice(liked_games)
        # print('random game', random_liked_game)

        """ check all other users with that game on their lists who liked the game as well (8 or higher?) """

        users_with_game_liked = (
            db.session.query(UsersGames)
            .filter(UsersGames.score >= 8)
            .filter_by(game_id=random_liked_game)
            .all()
        )
        # print('users who also like', users_with_game_liked)

        """check all other games on those users lists, and grab all with ratings of 6? or above"""
        df = pd.DataFrame()
        for user in users_with_game_liked:
            all_user_games = pd.read_sql(
                db.session.query(UsersGames).filter_by(user_id=user.user_id).statement,
                db.session.bind,
            )
            df = pd.concat([df, all_user_games])

        df = df.dropna()
        df["score"] = df["score"].astype(int)
        df = df.drop(df[df.score < 6].index)
        # print('liked games on other users lists', df)

        if df.empty:
            print("empty")
            should_restart = True

        else:
            print("good")
            should_restart = False

            """ get count of occurance of those games across all of those lists (match game_ids)"""

            count_per_game = df["game_id"].value_counts()
            # print(count_per_game)

            count_per_game_index = df["game_id"].value_counts().index.tolist()
            # print(count_per_game_index)

            games = []
            for key, value in zip(count_per_game_index, count_per_game):
                game = Games.query.filter_by(_id=key).first()
                # print(game.title)
                games.append(game)
            # AT THIS STAGE, THE RECOMMENDER WOULD WORK

            # print(games)
            return games
    """get avg score per game_id on this list"""

    """ select the top 3 scores, and recommend on home page"""

    """ present as "you liked X game" we think you might like A, B, and C as well!"""


# print(recommend(102))
random_user = random.randint(1, 100)
print("user", random_user)
print(recommend(random_user))


def recommender_2():
    # similar game recs / by user with similar game ranks

    pass