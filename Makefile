
test:
	py.test -vvx --capture=sys ./tests

run:
	python3 ./wa_tilda_parser.py

app: run
