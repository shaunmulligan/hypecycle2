Followed this tutorial: https://hackernoon.com/how-to-set-up-fastapi-ormar-and-alembic

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