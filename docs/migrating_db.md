Followed this tutorial: https://hackernoon.com/how-to-set-up-fastapi-ormar-and-alembic

## Initialize:
```
$ alembic init migrations
```
The folder `migrations` can't exist yet. Then set the db URL in alembic.ini:
```
sqlalchemy.url = sqlite:///db.sqlite
```

## create the migration script. 
```
$ alembic revision --autogenerate -m "Added users table"
```

## Run migrations
```
$ alembic upgrade head
```

## Tips:
- You can't drop/change a column easily with sqlite.
- to check SQL: `sqlite db.sqlite`