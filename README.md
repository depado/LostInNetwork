Lost In Network
=============
A web application to manage and detect security flaws on devices on a network.
Installation
---------------
First of all, download the archive or clone the repository. You will have nearly everything to work out of the box as soon as this is done.   

**Required Python version : Python 3.x**  
*For now this version only supports Python 3.x. This may change later.*   

If you don't have the `virtualenv` software on your computer you might want to install it.  

Create the virtualenv and install the dependencies as follow :

    cd path/where/you/cloned/the/repo
    virtualenv --no-site-packages venv
    source venv/bin/activate
    pip install -r requirements.txt
There are some things to note here. First of all you may check what Python version the virtualenv software will install. It must be a 3.x version. If it's not, please install Python 3.x (the latest stable version will do) and make sure the python version installed in the virtualenv fits. The command **may** be called virtualenv-3.x. Another thing is that maybe you don't have `pip` installed in your virtualenv. To fix that `easy_install pip`.  

**All the following commands and things described in this README needs to be done or executed with the activated virtualenv. Otherwise it may not work at all or won't have the expected behaviour.**

You need the config.py file. There is one in the repo that is encrypted. You have to decrypt it with the appropriate passphrase.

**If (and only if)** there is already a database in the repo, you can skip the database creation step (for now there is no database in the repo)  

To create the database, do as follow :

    python manage.py shell
    > from app import db
    > db.create_all()

You can then run your test server as follow :

    python manage.py runserver

Production
--------------
For a production run and environment you will have to set `DEBUG=False` in your settings file. A gunicorn configuration is provided for this use. **DO NOT** use `manage.py runserver` in a production environment. 

 
