Back/Front end for the WordsInMovies website - a search tool for language learners, teachers and experts in linguistics.

The main objective of the WordsInMovies website is to show how the translation (and the meaning!) of a given word 
varies depending on the situational context. 

The source for the WordsInMovies website is large film subtitles archives from the OpenSubtitles OPUS corpus 2018 
(http://opus.nlpl.eu/OpenSubtitles-v2018.php). 

More information about the website can be found in wordsinmovies_main/templates/wordsinmovies_main/about.html

The backend is written on Python 3.7 backed by the Django 3.0.2 framework.

Run the command source wim_env/bin/activate to activate the virtual environment, 
then python3 manage.py runserver to test

For complete functionality, the site needs the sphinx 3.2.1 engine installed and configured as well as 
a MySQL server with the generated databases. 

Look into the subtitles_databases project to learn how to build the databases and configure Sphinx.
