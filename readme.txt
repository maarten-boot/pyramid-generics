<include package="pyramid_jinja2" />

===============================================================================
Documentation: https://docs.pylonsproject.org/projects/pyramid/en/latest/
Tutorials:     https://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/
Twitter:       https://twitter.com/PylonsProject
Mailing List:  https://groups.google.com/forum/#!forum/pylons-discuss
Welcome to Pyramid.  Sorry for the convenience.
===============================================================================

Change directory into your newly created project.
    cd your_project_name

Create a Python virtual environment.
    python3 -m venv env

Install the project in editable mode with its testing requirements.
    env/bin/pip install -e ".[testing]"

Initialize and upgrade the database using Alembic.
    # Generate your first revision.
    env/bin/alembic -c development.ini revision --autogenerate -m "init"
    # Upgrade to that revision.
    env/bin/alembic -c development.ini upgrade head

Load default data into the database using a script.
    env/bin/initialize_your_project_name_db development.ini

Run your project's tests.
    env/bin/pytest

Run your project.
    env/bin/pserve development.ini

