# mygameslist-public

## What Is This Project?
Think IMDB or MAL, but for video games. 

It is a website. On it, a user may create a list of their favorite games, games they want to play, and so on. Users may view each-others lists, make suggestions for each other, comment and interact on the forums, and find fresh game suggestions generated via a suggestion system built on collaberative filtering.
 
---

## Preview

Note: recording software is hiding some dropdown menues. [begins at 0:57 in first video]



https://user-images.githubusercontent.com/96399096/204991206-c783e491-35b7-4112-a1bc-16806bb948cc.mov


https://user-images.githubusercontent.com/96399096/204991216-fa8bf13e-b4ea-4097-bf7a-c5506bc8097a.mov



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
#### Root
* app start-up via wsgi.py
* configs are in app.py

#### Folders
* **/ templates:** base html templates, and js rendering dynamically via app.context_processor 
* **/ static:** js libraries, css stylesheets, and profile pics
* **/ objects:** flask HTML forms, database objects, game recommender
* **/ blueprints:** sub-folders containing related HTML, flask routing, and utils
* **/ admintools:** loggers, flask admin setups
