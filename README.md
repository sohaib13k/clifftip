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


### Report upload conventions
|Report name|ferquency|file name format|
|-|-|-|
|sales purchase|monthly|