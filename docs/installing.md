# Python setup:
add `export PATH="$HOME/.local/bin:$PATH"` to bottom of `~/.bashrc`
pip3 install --user pipx

# Bring up DB:
To create all the empty tables in the DB, first run the db script stand alone
```
python3 model/db.py
```