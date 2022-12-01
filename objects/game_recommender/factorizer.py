import numpy as np
import pandas as pd

from objects.game_recommender.user_item_matrix import matrix_gen
from objects.db_objects.recommended_games import RecommendedGames
from objects.db_objects.users import Users
from objects.db_objects.users_games import UsersGames

from app import db
from admintools.loggers import logger_setup

logger = logger_setup(__name__, "log.log")



# TODO auto-schedule once per day or something? to run for every user? OR:
# TODO every time a single user adds a game, re-run the factorization for THEIR row in the matrix?


def factorizer():
    def matrix_factorization(R, P, Q, K, steps=1000, alpha=0.0002, beta=0.02):
        Q = Q.T
        for step in range(steps):
            for i in range(len(R)):
                for j in range(len(R[i])):
                    if R[i][j] > 0:
                        eij = R[i][j] - np.dot(P[i, :], Q[:, j])
                        for k in range(K):
                            P[i][k] = P[i][k] + alpha * (
                                2 * eij * Q[k][j] - beta * P[i][k]
                            )
                            Q[k][j] = Q[k][j] + alpha * (
                                2 * eij * P[i][k] - beta * Q[k][j]
                            )
            eR = np.dot(P, Q)
            e = 0
            for i in range(len(R)):
                for j in range(len(R[i])):
                    if R[i][j] > 0:
                        e = e + pow(R[i][j] - np.dot(P[i, :], Q[:, j]), 2)
                        for k in range(K):
                            e = e + (beta / 2) * (pow(P[i][k], 2) + pow(Q[k][j], 2))
            if e < 0.001:
                break
        return P, Q.T

    matrix = matrix_gen()
    R = matrix
    R = np.array(R)
    N = len(R)
    M = len(R[0])
    K = 2
    P = np.random.rand(N, K)
    Q = np.random.rand(M, K)
    nP, nQ = matrix_factorization(R, P, Q, K)
    nR = np.dot(nP, nQ.T)

    df = pd.DataFrame(nR, columns=[x for x in range(1, len(matrix.columns) + 1)])
    df.index += 1

    # must set new df index as matrix index, which results in index equaling the proper user_id
    df = pd.DataFrame(
        df.columns.values[np.argsort(-df.values, axis=1)[:, :30]], index=matrix.index
    )

    print(df)

    for i in range(0, len(df.index + 1)):
        # print("User ID", df.index[i])
        user_id = df.index[i]

        user = Users.query.filter_by(_id=int(user_id)).first()
        # print("DB USER", user)

        user_recommendations = df.loc[user_id]

        # print(user_recommendations)

        games = []
        # block ensures recommended game is not already on user list.
        for game_id in user_recommendations:
            user_list_checker = UsersGames.query.filter_by(
                user_id=user._id, game_id=game_id
            ).first()
            if user_list_checker:
                pass
            else:
                games.append(game_id)
            if len(games) == 10:
                print(user_id, "recs done")
                break

        # transforming game list into string to be passed to sql
        games = " ".join(str(i) for i in games)

        """  note: storing list of recommended games as a string in a single column
        this allows for being unpacked into list when needed,
        for simple implementation of randomly selecting x num of game_ids from the list to serve to users """

        user_finder = RecommendedGames.query.filter_by(user_id=user._id).first()
        if user_finder:
            user_finder.game_recommendations = games
        else:
            adder = RecommendedGames(user_id=user._id, game_recommendations=games)
            db.session.add(adder)

    db.session.commit()
    logger.info("FINISHED FACTORIZER")

if __name__ == "__main__":
    factorizer()
