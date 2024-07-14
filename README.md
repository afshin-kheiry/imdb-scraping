# imdb-scraping
serving scraped data from imdb with fastapi

## Installation
```
python -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt
cd base
python ../movies/scraper.py
uvicorn main:app --reload
```

you also need .env with following keys in it:
```
DRIVER_PATH
PROFILE_PATH
SQLALCHEMY_DATABASE_URL
SECRET_KEY
```

