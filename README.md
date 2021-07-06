# health-tech-demo

This is a project I've been working on during my 1B Co-op Term at SEEEG Data Inc.
It's a Django-based web service that aids in facilitating patient-doctor connections and appointment scheduling.
This app uses built-in Django authentication with a custom User Model, as well as Microsoft Graph and MSAL to connect to users' MS accounts and create Calendar events.
Other main dependencies are APScheduler for recurring tasks, MS Azure for Web App Hosting and Static File Blob Storage, and AWS for Database Storage and Connection.

As of now, the demo version of this app is hosted on Azure App Services and uses an AWS RDS PostgreSQL database (I know, poor practice to use two different cloud services, but they're hosted in the same region and AWS gave a 12 month free option, okay?)

Here's a breakdown of the apps contained in the root project folder:

- doctorappointment
    * A bit misleading and prone to renaming, this is sort of the index. It contains functionalities that are accessible to users of all groups, such as the homepage and about us page.
- accounts
    * Contains all our User Models, including the custom Base User and Proxy Models for Patients and Doctors
    * Also contains Form templates for registration and editing profiles (login is Django built-in, but styled in the template)
- book
    * This app handles the booking process and most functions involving appointment management, everything from when a Doctor decides to open a timeslot for potential appointments to when a Patient books an available slot.
    * Also contains our model for Appointments, as well as the Form templates
- appointment
    * I know, I'm horrible at naming these, but this is the app that takes care of one-to-one appointment details, such as notes and prescriptions.
    * Pretty basic, contains a model for appointment details, and nowhere near as big as book or account
- scheduledreminders
    * Self explanatory, handles the sending of scheduled reminders.
    * Regularly checks database using APScheduler for any upcoming appointments (< 15 minutes) and uses Django send_mail to send email and SMS notifications.
- graph
    * Everything pertaining to MS Graph connections and API usage, including authentication using OAuth 2.0, getting user profile info and creating events on Outlook Calendar.
    * Most functions are from MS Graph documentation [found here](https://docs.microsoft.com/en-us/graph/tutorials/python).
- maps
    * Helper app that handles usage of the Google Maps REST API
    * Specifically, Places API, Embed Map API and Geocode API
