from sqlalchemy import desc
import humanize
from collections import Counter

from objects.db_objects.posts import Posts
from objects.db_objects.comments import Comments

""" strings for parsing humanized time periods. popularity is measured by how often 
seconds/minutes/hours/days arises in the humanized time return. 
"""

# TODO factor recency of post itself

def popular_posts_getter(posts):
    days_string = "days"
    hours_string = "hours"
    second_string = "second"
    minute_string = "minute"
    recently_active = {}
    for post in posts:
        num_recent_hours = 0
        num_recent_days = 0
        num_recent_seconds = 0
        num_recent_minutes = 0

        comments = post.comments.order_by(desc("date_posted")).limit(10)

        for comment in comments:
            relative_time = humanize.naturaltime(comment.date_posted)

            if relative_time.find(hours_string) != -1:
                num_recent_hours += 1
            elif relative_time.find(days_string) != -1:
                try:
                    value = int(str(relative_time)[:2])
                    if value < 7:
                        num_recent_days += 0.5
                    else:
                        num_recent_days += 0.2
                except ValueError as e:
                    num_recent_days += 0.7
            elif relative_time.find(second_string) != -1:
                num_recent_seconds += 1
            elif relative_time.find(minute_string) != -1:
                num_recent_minutes += 1
        recently_active[post._id] = (
            num_recent_seconds,
            num_recent_minutes,
            num_recent_hours,
            num_recent_days,
        )

    weighted_popularity = {}
    for key, value in recently_active.items():
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
    top_3 = counter.most_common(3)
    popular_posts = []
    for i in top_3:
        popular_post = Posts.query.filter_by(_id=i[0]).first()
        popular_posts.append(popular_post)

    # print(weighted_popularity)
    # print(popular_posts)
    return popular_posts


if __name__ == "__main__":
    post = Posts.query.all()
    popular_posts_getter(post)
