# GYMVision

Virtual gym with automatic posture corrections powered by computer vision (MediaPipe and OpenCV).

Django PWA to engage users in to start exercising at their houses providing: pose correction, gamification, calendars, alarms...

## Installation and executing PWA

To install the required dependencies:
```bash
  pip install -r requirements.txt 
```
To start the server: 

```bash
  python manage.py runserver
```

To start the server with a specific ip:port:
```bash
  python manage.py runserver a.b.c.d:port
```

To initialize database: 
Make sure to delete db.sqlite3 if exists
 
```bash
  python manage.py migrate --run-syncdb
  python manage.py loaddata datos
```

After initializing database, create database superuser [user: admin] [passwd: admin] to access to access http://ip:port/admin and see all tables with data:
```bash 
  echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')" | python manage.py shell
```