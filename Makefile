VERSION=$(shell python3 -c "from configparser import ConfigParser; p = ConfigParser(); p.read('setup.cfg'); print(p['metadata']['version'])")

default:
	@echo "\"make publish\"?"

upload: clean
	@if [ "$(shell git rev-parse --abbrev-ref HEAD)" != "master" ]; then exit 1; fi
	# python3 setup.py sdist bdist_wheel
	# https://stackoverflow.com/a/58756491/353337
	python3 -m build --sdist --wheel .
	twine upload dist/*

update:
	python3 data/update.py -t ~/.github-access-token

nschloe:
	 stargraph nschloe/tikzplotlib nschloe/meshio nschloe/perfplot nschloe/quadpy nschloe/betterbib nschloe/pygmsh nschloe/tuna nschloe/awesome-scientific-computing nschloe/termplotlib nschloe/optimesh matlab2tikz/matlab2tikz -m 30 -t ~/.github-access-token -o nschloe.svg

tag:
	@if [ "$(shell git rev-parse --abbrev-ref HEAD)" != "master" ]; then exit 1; fi
	# Always create a github "release"; this automatically creates a Git tag, too.
	curl -H "Authorization: token `cat $(HOME)/.github-access-token`" -d '{"tag_name": "v$(VERSION)"}' https://api.github.com/repos/nschloe/stargraph/releases

publish: tag upload

clean:
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$\)" | xargs rm -rf
	@rm -rf *.egg-info/ build/ dist/ MANIFEST .pytest_cache/

format:
	isort .
	black .

lint:
	isort --check .
	black --check .
	flake8 .
