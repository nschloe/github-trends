version := `python3 -c "from configparser import ConfigParser; p = ConfigParser(); p.read('setup.cfg'); print(p['metadata']['version'])"`
name := `python3 -c "from configparser import ConfigParser; p = ConfigParser(); p.read('setup.cfg'); print(p['metadata']['name'])"`

default:
	@echo "\"make publish\"?"

upload: clean
	@if [ "$(git rev-parse --abbrev-ref HEAD)" != "main" ]; then exit 1; fi
	# python3 setup.py sdist bdist_wheel
	# https://stackoverflow.com/a/58756491/353337
	python3 -m build --sdist --wheel .
	twine upload dist/*

update:
	python3 data/update.py -t ~/.github-access-token

tag:
	@if [ "$(git rev-parse --abbrev-ref HEAD)" != "main" ]; then exit 1; fi
	# Always create a github "release"; this automatically creates a Git tag, too.
	curl -H "Authorization: token `cat ~/.github-access-token`" -d '{"tag_name": "v{{version}}"}' https://api.github.com/repos/nschloe/{{name}}/releases

publish: tag upload

clean:
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
	@rm -rf src/*.egg-info/ build/ dist/ .tox/

format:
	isort .
	black .

lint:
	isort --check .
	black --check .
	flake8 .
