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


### TODO
1. Currently /ddr categorises, logic/view based on individual report. Means each report will have it's own logic function and view template. This is based on assumption that each report is unique in itself with different view-expectation from director. But later if this is not the case, then views/logic will be merged to remove code duplicacy; like let's say for some 20 reports, directors only sees the total amount, then these 20 logic/view will be merged. 
