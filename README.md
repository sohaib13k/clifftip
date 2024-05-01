### Pre-requisite
1. .env placement in base directory. Secret key can be generated using below code.

```bash
DEBUG=True
SECRET_KEY="5t36rsv1_(-$q025a!7_=(*sbsij^dss_)8v&znnr5kzqgroz0"
```
```python
from django.core.management.utils import get_random_secret_key  
get_random_secret_key()
```

2. adding wsgi configuration as per below.
### wsgi configuration for pythonanywhere depoyment

```python
from dotenv import load_dotenv
load_dotenv(dotenv_path=path + '/.env') # path is projects root-dir. or base-dir.
```


### Deployment steps
1. Create virtual env.
2. Install dependencies from requirements.txt
3. Install nginx
```bash
4. gunicorn --bind 0.0.0.0:8000 wsgi:application
```
5. Remove the default server block. Create a new configuration file in /etc/nginx/sites-available/ and symlink it to /etc/nginx/sites-enabled/
6. Set up Nginx to proxy requests to Gunicorn:
```bash
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
```bash
7.1 sudo nginx -t
7.2 sudo systemctl restart nginx
8. sudo snap install --classic certbot
9. sudo certbot --nginx
10. python manage.py collectstatic
11. python manage.py migrate
12. python manage.py createsuperuser
```

### Report upload conventions
|Report name|ferquency|req.|
|-|-|-|
|sales purchase|monthly|4th row contains header. (Customer GSTN)|
|all_parties|NA|it should be in xls/xlsx. 2 branch column; first one to be removed.|


### Points
1. Adding a new report or creating a view, below places to be updated-
1.1. report.service.data_frame.py
1.2. report.service.report_logic.py
1.3. Create a view with same name