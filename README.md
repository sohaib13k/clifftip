### Pre-requisite
1. .env placement in base directory. Secret key can be generated using below code.

```bash
DEBUG=True
SECRET_KEY="5t36rsv1_(-$q025a!7_=(*sbsij^dss_)8v&znnr5kzqgroz0"
ALLOWED_HOSTS="clifftip.mavensoft.in"
LOG_LOCATION="/var/log/gunicorn/django.log"

MSSQL_HOST="clifftip.database.windows.net"
MSSQL_DB_NAME="erp-dump-clifftip"
MSSQL_USERNAME="laughing-elephant"
MSSQL_PASSWORD=""
MSSQL_PORT="1433"
MSSQL_DRIVER="ODBC Driver 17 for SQL Server"

AZURE_STORAGE_CONNECTION_STRING=""
AZURE_STORAGE_CONTAINER_NAME="clifftip-erp-backup"

# AZURE_STORAGE_ACCOUNT_NAME=""
# AZURE_STORAGE_ACCOUNT_KEY=""
# AZURE_STORAGE_CONTAINER_NAME=""

```
```python
from django.core.management.utils import get_random_secret_key  
get_random_secret_key()
```

2. adding wsgi configuration as per below.
### wsgi configuration

```python
from dotenv import load_dotenv
load_dotenv(dotenv_path=path + '/.env') # path is projects root-dir. or base-dir.
```


### Deployment steps
0. sudo timedatectl set-timezone Asia/Kolkata
1. Create virtual env.
2. Install dependencies from requirements.txt
3. Install nginx
```bash
4.0 gunicorn clifftip.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile /var/log/gunicorn/access.log --error-logfile /var/log/gunicorn/error.log &
4.1 When git pull- 
4.1.1 pkill gunicorn
4.1.3 sudo systemctl restart nginx
```
5. Remove the default server block. Create a new configuration file in /etc/nginx/sites-available/ and symlink it to /etc/nginx/sites-enabled/
6. Set up Nginx to proxy requests to Gunicorn:
```bash
server {
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_proxied any;
    gzip_min_length 256;
    gzip_vary on;
    gzip_disable "msie6";
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;
    
    server_name clifftip.mavensoft.in;

    client_max_body_size 200M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/clifftip/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location /favicon.ico {
        alias /var/www/clifftip/img/favicon.ico;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
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
13. Azure mssql server provision
14. Install necessary dependencies - https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=ubuntu18-install%2Calpine17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline#18

### Report upload conventions
|Report name|ferquency|req.|
|-|-|-|
|sales purchase|monthly|4th row contains header. (Customer GSTN)|
|all_parties|NA|it should be in xls/xlsx. 2 branch column; first one to be removed.|


### Points
1. Adding a new report or creating a view, below places to be updated-
1.1 report.service.data_frame.py
1.2 report.service.report_logic.py
1.3 report.service.upload_check.py (optional)
1.4 Create a view with same name

### CI CD script
```bash
cd
tar -czf bckp/clifftip.backup.tar.gz projects/clifftip/
cd /root/projects/clifftip/clifftip
source ../.virtualenv/bin/activate
git reset --hard
git clean -df
git pull
echo "yes" | python manage.py collectstatic
sudo rm -r /var/www/clifftip
sudo mv ~/projects/clifftip/static/ /var/www/clifftip/
gunicorn clifftip.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 300 --access-logfile /var/log/gunicorn/clifftip/access.log --error-logfile /var/log/gunicorn/clifftip/error.log &
sudo systemctl restart nginx
```

### Adding a new company/login
1. Add company enum in account.models.User.Company
1.1. Create company user model inheriting User. Create model manager
2. Addin company enum in report.models.Report.Company
3. Create admin panel and register user model, earlier created
3.1. Create report admin panel and register in admin panel
3.2. Add admin panel route in clifftip.urls.py
4. Create a superuser
4.1. open shell/db and set user.company="new_company_enum"
5. In navbar.html and sidebar.html, change company name and route to admin panel