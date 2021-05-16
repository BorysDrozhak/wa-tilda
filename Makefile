
test:
	py.test -vvx --capture=sys ./tests

run:
	python ./wa_tilda_parser.py

app: run
