# mygameslist-public
 
---

## Preview
video of running


---

## Demo
link to host

RUNNING LOCALLY:
* Install requirements outlined in requirements.txt
* Run via wsgi.py file

---

### Features
* Automated collaborative recommendation system for games using matrix factorization.
* Algorithms to gauge popularity of forum posts, and of games on site.
* List and rate your favorite games.
* User-generated similar games or recommended games.
* Forum posts with comments, likes, dislikes, and links to games, users, or other forum posts.
* Register, login, edit, and delete user accounts.
* Reset account passwords via email.
* Type-ahead search bar with full text search.
* Filtering system for forum posts and game lists.

---

### Project Structure
* app start-up via wsgi.py
* configs are in app.py

/ / / / / /

* **/ templates:** base html templates, and js rendering dynamically via app.context_processor 
* **/ static:** js libraries, css stylesheets, and profile pics
* **/ objects:** flask HTML forms, database objects, game recommender
* **/ blueprints:** sub-folders containing related HTML, flask routing, and utils
* **/ admintools:** loggers, flask admin setups