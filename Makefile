FILES = *.py
LINE_LENGTH = 160

# -i E501,C0114,C0115,C0116,C0301,R1705,R0903,W0603,W1510,C0103,W0613
# C0103 Variable name "XX" doesn't conform to snake_case naming style
# C0114 Missing module docstring
# C0115 Missing class docstring
# C0116 Missing function or method docstring

all: format

format: black pylama mypy

black:
	source ./env/bin/activate; \
	black \
		--line-length $(LINE_LENGTH) \
		$(FILES) models/$(FILES) views/$(FILES)

pylama:
	source ./env/bin/activate; \
	pylama --max-line-length=$(LINE_LENGTH) \
		--linters "eradicate,mccabe,pycodestyle,pyflakes,pylint" \
		--ignore C0103,C0114,C0115,C0116 \
		$(FILES) models/$(FILES) views/$(FILES)

mypy:
	source ./env/bin/activate; \
	mypy \
		--strict \
		--no-incremental \
		$(FILES) models/$(FILES) views/$(FILES)

s1:
	bash s1.sh
