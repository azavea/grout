### Migrations

Before creating a migration, read this:
http://alembic.readthedocs.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect

Ok cool. Now, update tables in `ashlar/models.py`

Then run: `alembic revision --autogenerate -m "Your commit message here"`
NOW, AS PER THE RULES ABOVE, MANUALLY INSPECT THE CREATED MIGRATION FILE!

Finally, `alembic upgrade head`

