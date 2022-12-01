from sqlalchemy import desc
import humanize
from collections import Counter

from objects.db_objects.users_games import UsersGames
from objects.db_objects.games import Games
from objects.db_objects.category import Category
from objects.db_objects.games_categories import GamesCategories

""" strings for parsing humanized time periods. popularity is measured by how often 
seconds/minutes/hours/days arises in the humanized time return. 
"""


def popular_games_getter(listed_games):
    days_string = "day"
    hours_string = "hours"
    second_string = "second"
    minute_string = "minute"

    num_recent_hours = 0
    num_recent_days = 0
    num_recent_seconds = 0
    num_recent_minutes = 0

    games_popularity = {}
    for game in listed_games:
        relative_time = humanize.naturaltime(game.date_added)

        if relative_time.find(hours_string) != -1:
            num_recent_hours += 1
        elif relative_time.find(days_string) != -1:
            try:
                value = int(str(relative_time)[:2])
                if value < 7:
                    num_recent_days += 0.5
                    # print(value, "+2")
                else:
                    num_recent_days += 0.2
                    # print(value, "+1")
            except ValueError as e:
                num_recent_days += 0.7

        elif relative_time.find(second_string) != -1:
            num_recent_seconds += 1
        elif relative_time.find(minute_string) != -1:
            num_recent_minutes += 1
        games_popularity[game.game_id] = (
            num_recent_seconds,
            num_recent_minutes,
            num_recent_hours,
            round(num_recent_days),
        )

    # print(games_popularity)

    weighted_popularity = {}
    for key, value in games_popularity.items():
        # weight for humanized returns in "Seconds" is highest, while "days" is lowest.
        weighted_total = 0
        for i in range(value[0]):
            # SECONDS
            weighted_total += 20
        for i in range(value[1]):
            # MINUTES
            weighted_total += 10
        for i in range(value[2]):
            # HOURS
            weighted_total += 5
        for i in range(round(value[3])):
            # DAYS
            weighted_total += 2
        weighted_popularity[key] = weighted_total

    counter = Counter(weighted_popularity)
    top_20 = counter.most_common(50)
    popular_games = []
    # top_3 = 0
    top_9 = 0

    for i in top_20:
        game = Games.query.filter_by(_id=i[0]).filter(Games.average_score > 6).first()
        if game is None:
            # print(game)
            pass
        else:
            popular_games.append(game)
            top_9 += 1
            if top_9 == 9:
                break

    # print(weighted_popularity)
    # print(popular_games)
    return popular_games


if __name__ == "__main__":
    listed_games = UsersGames.query.all()
    popular_games_getter(listed_games)
