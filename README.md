# steamwatcher
This application aims at people who would like to have further information about their own or their friends steam usage statistics. To achieve that this project consists of multiple parts from a analysis and query script up to an user frontend (web-based, Android, ...). The following chapters will give you further information about what is needed to set everything up correctly and how to access the frontend parts.

What this project mainly consists of:
- Python script that is started by a cronjob regularly 
 - which requests the data from the steam backend
 - analysis the data
 - stores the results in a database
- Python script that servers as a RESTful backend API
- Frontend services
 - Web-Frontend based upon Bootstrap and Google Charts
 - Smartphone Apps (Android, Windows Phone, iOS)

# prerequisites
There are different programs that need to be installed on your server.
- python 2.7 (3.x untested yet)
- mysql-server
- webserver (i.e. apache2 or lighttpd)
- cronjobs
- Steam API key

# configuration
- Enable database connection
- Import SQL layout from repo
- Configure cronjob
- Configure webserver (optional)
- Configure python modules (...)
- Get a Steam API key

# setup & startup
Start the python REST API by using ...
