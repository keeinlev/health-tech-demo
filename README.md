# health-tech-demo

This is a project I've been working on during my 1B Co-op Term at SEEEG Data Inc.
It's a Django-based web service that aids in facilitating patient-doctor connections and appointment scheduling.
This app uses built-in Django authentication with a custom User Model, as well as Microsoft Graph and MSAL to connect to users' MS accounts and create Calendar events.
Other main dependencies are APScheduler for recurring tasks, MS Azure for Web App Hosting and Static File Blob Storage, and AWS for Database Storage and Connection.

As of now, the demo version of this app is hosted through Azure App Services, static and media files are stored in an Azure Storage Account, and app data is stored in an AWS RDS PostgreSQL database. It was much simpler to set up a free SQL database with AWS, plus using multiple cloud services can also be an added layer of resiliency.

# [Try the Demo here](https://health-tech.azurewebsites.net/)

---

# Table of Contents
- [Overview of Packages](#overview-of-packages)
- [Deploying to Azure](#deploying-the-app-to-the-azure-cloud)
- [Running the Application Locally](#running-the-application-on-your-local-machine)
- [Accessing the Admin Page](#accessing-the-admin-page)
- [Required Libraries](#required-libraries)

---

# Overview of Packages

Here's a breakdown of the packages (Django apps) contained in the root project folder:

- health
    * Project folder, contains the app's settings.
        - settings.py defines general settings
        - development.py and production.py set the allowed hosts, DEBUG and domain settings, production.py also sets CSRF and Cookie settings
        - development_db_settings.py sets the app to store data in a local SQLite database
        - production_db_settings.py sets the app to store data in an external database (currently set to use AWS RDS PostgreSQL)
        - development_storage_settings.py sets the app to store static files and media in local directories
        - production_storage_settings.py sets the app to store static files and media in an external storage system (currently set to use Azure Storage Account)
        - development.py and development_db_settings.py will be active if DJANGO_DEVELOPMENT (environment variable)/DEBUG (setting) are set to True, while production.py and production_db_settings.py will be active otherwise
        - development_storage_settings.py will be active if DJANGO_EXT_STORAGE (environment variable) is set to False and production_storage_settings.py will be active otherwise
    * manage.py can be used to run Django commands in-console (does essentially the same thing as django-admin as seen [here](https://docs.djangoproject.com/en/3.2/ref/django-admin/#available-commands))
    * All main routing paths can be found in urls.py
    * Also contains modified templates for default views such as login and password reset
- home
    * This is sort of the index. It contains functionalities that are accessible to users of all groups, such as the home, about us and error pages.
- accounts
    * Contains all our User Models, including the custom Base User and Proxy Models for Patients and Doctors
    * Also contains Form templates for registration and editing profiles (login is Django built-in, but styled in the template)
- book
    * This app handles the booking process and most functions involving appointment management, everything from when a Doctor decides to open a timeslot for potential appointments to when a Patient books an available slot.
    * Also contains our model for Appointments, as well as the Form templates
- doctordashboard
    * Pertains to all the main functions available to Doctor users, which are all accessible from the dashboard page
    * Very intertwined with the book app and makes lots of additions and changes to Appointment objects.
- appointment
    * Takes care of appointment files and details such as notes and prescriptions.
    * Contains models for appointment details and files, and nowhere near as big as book or account
        - Note: Does not contain the Appointment model, which may cause confusion
        - This was created later into development to hold models that are auxilliary to the main Appointment model and the associated views, while the main model is defined in the book app and is referenced in almost every app. However, most of its related views are located in book or doctordashboard.
- patientdashboard
    * Much simpler than the doctordashboard app, as this serves to only view Appointment details as a Patient and the upload/get/delete processes for images.
- scheduledreminders
    * Self explanatory, handles the sending of scheduled reminders.
    * Regularly checks database using APScheduler for any upcoming appointments (15 minutes ahead) and uses Django send_mail to send email and SMS notifications.
- graph
    * Everything pertaining to MS Graph connections and API usage, including authentication using OAuth 2.0, getting user profile info and creating events on Outlook Calendar.
    * Most functions are from MS Graph documentation [found here](https://docs.microsoft.com/en-us/graph/tutorials/python).
- maps
    * Helper app that handles usage of the Google Maps REST API
    * Specifically, Places API, Embed Map API and Geocode API
- customstorage
    * Very basic app which allows for differentiating between public and private Azure Storage objects, taken from [here](https://django-storages.readthedocs.io/en/latest/backends/azure.html)

---

# Deploying the Application to the Cloud

Please see the Dev Guide in the repository

---

# Running the Application on your local machine

In order to get this app up and running locally on your machine, please take the following steps:

1. Ensure you are running at least Python version 3.8
2. Download all source files from the repository to a virtual environment directory (recommended) or any local directory
    ex. 'C:\Users\Name\Documents\Projects\This_Repo'
3. Install the required Python modules if they are not yet installed on your machine.
    - If on Linux, run sudo apt-get install --reinstall libpq-dev
    - Note: this can be done by running pip install -r requirements.txt
4. Set all the required environment variables in a .env file, located in the 'health' module, the same folder as settings.py.
5. Open a command line interface (i.e. cmd, powershell, etc) and navigate to the outer 'health' directory found in the cloned repository's folder
    ![cmd-cd](/screenshots/cmdline1.png/)
6. Once in the 'health' folder, run the following commands in the command line:
    ```
    python manage.py migrate
    ```
    and
    
    ```
    python manage.py runserver
    ```
    
    If successful, the following message should appear:
    ![run-success](/screenshots/runsuccess.png/)

7. In a browser, open the following link: http://127.0.0.1:8000/
8. You're all set! To stop the server, press Ctrl + C

---

# Accessing the Admin Page

The Admin Page allows the user to look through, edit and delete the database entries from the app.  
In order to access it, use the following steps:  

1. Navigate to the 'health' directory as shown in [Running the Application](#running-locally)
2. If already in the 'health' directory, shut down the server with Ctrl + C if it is still running
3. Create a super user with the following command in command line:
    ```
    python manage.py createsuperuser
    ```
4. Enter some login credentials
    ![superuser](/screenshots/superuser.png)
    
    If successful, the following message should appear:
    ```
    Superuser created successfully.
    ```

5. Run the server again using 'python manage.py runserver'

6. Go to the following link in your browser: http://127.0.0.1:8000/admin and enter your login credentials
    ![superlogin](/screenshots/sulogin.png)  

7. You're in! Take a look around, create, edit or delete entries from here.  

---

# Required Libraries
A list of all Python libraries on which the app is dependent and their minimum versions can be found in the requirements.txt file

It is recommended that you install these libraries within a virtual environment

To install all required libraries, activate the virtual environment (if applicable), navigate to the same directory as the requirements.txt file, and execute the following in the command line:

```
pip install -r requirements.txt
```