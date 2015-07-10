all:
	@echo "make env"
	@echo "make deps"

env:
	virtualenv-2.7 --no-site-package venv

deps:
	source venv/bin/activate && pip install -r requirements.txt

server:
	python manager.py runserver

database:
	alembic upgrade head

redis:
	redis-server /usr/local/etc/redis.conf

schedule:
	celery worker -E -l INFO -n task -A taut.tasks.schedule -B

task:
	celery worker -E -l INFO -n task -A taut.tasks.dropbox

event-celery-bin:
	celery events -A taut.tasks.schedule.celery

thumb:
	cp thumbor/loaders/twimg.py venv/lib/python2.7/site-packages/thumbor/loaders/twimg.py
	thumbor -p 8888 -c ./taut/configs/thumbor.py

postgres:
	postgres -D /usr/local/var/postgres

sqlite2pg:
	alembic downgrade base && alembic upgrade head && cd etc && pgloader sqlite2pg.load && cd ..

clean: clean-pyc

clean-pyc:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
