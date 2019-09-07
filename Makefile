test:
	coverage run --source=. -m pytest ./_test/*.py
	coverage report -m

.PHONY: _test
