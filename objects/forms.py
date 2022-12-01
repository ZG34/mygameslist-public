import sqlalchemy.exc
from flask_wtf import FlaskForm
import re
from string import ascii_lowercase as letters

# wtf lets you use python classes to render html forms, rather than write in html
from wtforms import StringField, TextAreaField, SubmitField, EmailField, PasswordField, SelectField, HiddenField, \
    SelectMultipleField, FormField, Form, BooleanField
from wtforms.validators import DataRequired, Email, Length, Regexp

from objects.db_objects.category import Category
from objects.db_objects.games import Games

characters = [("", "Starts With:")]
for letter in letters:
    characters.append((letter.upper(), letter.upper()))

num_list = [x for x in range(0, 11)]
for num in num_list:
    characters.append((num, num))


# note that length validator does not throw an error if passed, but instead just prevent all inputs beyond max limit

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=3, max=50)])
    body = TextAreaField("Body", validators=[DataRequired(), Length(min=3, max=200)])
    submit = SubmitField("Post")


class ReplyForm(FlaskForm):
    body = TextAreaField("Body", validators=[DataRequired(), Length(min=3, max=200)])
    submit = SubmitField("Post Reply")


class LikeForm(FlaskForm):
    like = SubmitField("Like")
    dislike = SubmitField("Dislike")


class LikeForm2(FlaskForm):
    like = SubmitField("CommentLike")
    dislike = SubmitField("CommentDislike")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=1, max=30)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=26)])
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(min=3, max=320)])
    privacy = BooleanField("Privacy", validators=[DataRequired()])
    submit = SubmitField("Submit")


class RecoveryForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Send Recovery Message")


class AddGameForm(FlaskForm):
    status_choices = [("", ""), ('want to play', 'Want to Play'), ('completed', 'Completed'),
                      ('playing', 'Playing'), ('dropped', 'Dropped')]
    score_choices = [("", ""), (10, 10), (9, 9), (8, 8), (7, 7), (6, 6), (5, 5), (4, 4),
                     (3, 3), (2, 2), (1, 1)]

    status = SelectField("Status", choices=status_choices, validators=[DataRequired()])
    score = SelectField("Score", choices=score_choices)
    submit = SubmitField("Add to My Games")
    # hiddenfield is present to hold jinja query, fetching game_name to be passed later
    game = HiddenField()


class UpdateGameForm(FlaskForm):
    status_choices = [("", ""), ('want to play', 'Want to Play'), ('completed', 'Completed'),
                      ('playing', 'Playing'), ('dropped', 'Dropped')]
    score_choices = [("", ""), (10, 10), (9, 9), (8, 8), (7, 7), (6, 6), (5, 5), (4, 4),
                     (3, 3), (2, 2), (1, 1)]

    status = SelectField("Status", choices=status_choices, validators=[DataRequired()])
    score = SelectField("Score", choices=score_choices)
    submit = SubmitField("Add to My Games")
    # hiddenfield is present to hold jinja query, fetching game_name to be passed later
    game = HiddenField()

    # addition would be querying usergames and grabbing the existing score/status to display in k/v


class RecommendGameForm(FlaskForm):
    pass


class ForumFilterForm(FlaskForm):
    selector = SelectField("Selector", choices=["Date Posted", "Likes"])
    order_by = SelectField("Order_By", choices=["DESC", "ASC"])
    sort = SubmitField("Sort")


class GameSorter(Form):
    selector_choices = [('Games.ratings_count', 'Popularity'), ('Games.average_score','Avg. Rating')]
    order_by_choices = [('desc', 'DESC'), ('asc', 'ASC')]

    selector = SelectField("Selector", choices=selector_choices)
    order_by = SelectField("Order_By", choices=order_by_choices)


class FilterGamesForm(Form):
    category_titles = [(" ", "Category:")]
    try:
        categories = Category.query.all()

        for category in categories:
            category_titles.append((category.tag, category.tag))
    except sqlalchemy.exc.OperationalError as e:
        pass
    category_filter = SelectField("Category", choices=category_titles)
    starts_with = SelectField("Starts_With", choices=characters)


class MyListFilterForm(FlaskForm):
    status_choices = [("", "Status:"), ('want to play', 'Want to Play'), ('completed', 'Completed'),
                      ('playing', 'Playing'), ('dropped', 'Dropped')]
    category_titles = [(" ", "Category:")]
    try:
        categories = Category.query.all()
        for category in categories:
            category_titles.append((category.tag, category.tag))
    except sqlalchemy.exc.OperationalError as e:
        pass

    category_filter = SelectField("Category", choices=category_titles)
    starts_with = SelectField("Starts_With", choices=characters)
    status = SelectField("Status", choices=status_choices)
    # search = SubmitField("Search")


class BrowseForms(FlaskForm):
    # FIXME is this a site-changing operation? if yes, needs CSRF
    # currently passed forms are inheriting from FORM to prevent default CSRF to allow for clean GET
    # if need CSRF, change to POST, redirect to get after passing data, and re-add FlaskForm and CSRF token
    game_sorter = FormField(GameSorter)
    game_filter = FormField(FilterGamesForm)
    fullsearch = SubmitField("Apply Criteria")
    # submit element, to capture both forms


class MyListForm(FlaskForm):
    game_sorter = FormField(GameSorter)
    game_filter = FormField(MyListFilterForm)
    fullsearch = SubmitField("Apply Criteria")