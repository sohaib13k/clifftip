### wsgi configuration for pythonanywhere depoyment

```python
from dotenv import load_dotenv
load_dotenv(dotenv_path=path + '/.env')
```


### TODO
1. Currently /ddr categorises, logic/view based on individual report. Means each report will have it's own logic function and view template. This is based on assumption that each report is unique in itself with different view-expectation from director. But later if this is not the case, then views/logic will be merged to remove code duplicacy; like let's say for some 20 reports, directors only sees the total amount, then these 20 logic/view will be merged. 