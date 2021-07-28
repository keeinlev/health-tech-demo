# health-tech-demo

This is a project I've been working on during my 1B Co-op Term at SEEEG Data Inc.
It's a Django-based web service that aids in facilitating patient-doctor connections and appointment scheduling.
This app uses built-in Django authentication with a custom User Model, as well as Microsoft Graph and MSAL to connect to users' MS accounts and create Calendar events.
Other main dependencies are APScheduler for recurring tasks, MS Azure for Web App Hosting and Static File Blob Storage, and AWS for Database Storage and Connection.

As of now, the demo version of this app is hosted through Azure App Services, static and media files are stored in an Azure Storage Account, and app data is stored in an AWS RDS PostgreSQL database. It was much simpler to set up a free SQL database with AWS, plus using multiple cloud services can also be an added layer of resiliency.

Here's a breakdown of the modules contained in the root project folder:

- health
    * Project folder, contains the app's configurations in settings.py, development.py and production.py
    * manage.py can be used to run Django commands in-console (does essentially the same thing as django-admin as seen [here](https://docs.djangoproject.com/en/3.2/ref/django-admin/#available-commands))
    * All main routing paths can be found in urls.py
    * Also contains modified templates for default views such as login and password reset
- doctorappointment
    * This is sort of the index. It contains functionalities that are accessible to users of all groups, such as the home, about us and error pages.
- accounts
    * Contains all our User Models, including the custom Base User and Proxy Models for Patients and Doctors
    * Also contains Form templates for registration and editing profiles (login is Django built-in, but styled in the template)
- book
    * This app handles the booking process and most functions involving appointment management, everything from when a Doctor decides to open a timeslot for potential appointments to when a Patient books an available slot.
    * Also contains our model for Appointments, as well as the Form templates
- doctordashboard
    * Pertains to all the main functions available to Doctor users, which are all accessible from the dashboard page
    * Very intertwined with the book module and makes lots of additions and changes to Appointment objects.
- appointment
    * I know, I'm horrible at naming these, but this is the app that takes care of one-to-one appointment details, such as notes and prescriptions.
    * Pretty basic, contains a model for appointment details, and nowhere near as big as book or account
- patientdashboard
    * Much simpler than the doctordashboard module, as this serves to only view Appointment details as a Patient and the upload/get/delete processes for images.
- scheduledreminders
    * Self explanatory, handles the sending of scheduled reminders.
    * Regularly checks database using APScheduler for any upcoming appointments (< 15 minutes) and uses Django send_mail to send email and SMS notifications.
- graph
    * Everything pertaining to MS Graph connections and API usage, including authentication using OAuth 2.0, getting user profile info and creating events on Outlook Calendar.
    * Most functions are from MS Graph documentation [found here](https://docs.microsoft.com/en-us/graph/tutorials/python).
- maps
    * Helper app that handles usage of the Google Maps REST API
    * Specifically, Places API, Embed Map API and Geocode API
- customstorage
    * Very basic module which allows for differentiating between public and private Azure Storage objects, taken from [here](https://django-storages.readthedocs.io/en/latest/backends/azure.html)