
test:
	py.test -vvx --capture=sys ./tests

reqs:
	pip3 install -r requirements.txt

run:
	python3 ./wa_tilda_parser.py

app: run
