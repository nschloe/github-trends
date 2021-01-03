# gh-stars

[![gh-actions](https://img.shields.io/github/workflow/status/nschloe/gh-stars/ci?style=flat-square)](https://github.com/nschloe/gh-stars/actions?query=workflow%3Aci)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/gh-stars.svg?style=flat-square)](https://pypi.org/pypi/gh-stars/)
[![PyPi Version](https://img.shields.io/pypi/v/gh-stars.svg?style=flat-square)](https://pypi.org/project/gh-stars)
[![GitHub stars](https://img.shields.io/github/stars/nschloe/gh-stars.svg?style=flat-square&logo=github&label=Stars&logoColor=white)](https://github.com/nschloe/gh-stars)
[![PyPi downloads](https://img.shields.io/pypi/dm/gh-stars.svg?style=flat-square)](https://pypistats.org/packages/gh-stars)

gh-stars is a Python/command-line tool that collects the star count from [GitHub
stars](http://github.com/) and produces nice plots from it.

For example,
```
gh-stars nschloe/meshio nschloe/quadpy -m 30 -t file-with-gh-token -o nschloe.svg
```
gives

[github-nschloe](https://nschloe.github.io/gh-stars/nschloe.svg)

(GitHub and has a rate limit so you might want to get a token and provide it to
gh-stars.)

Install with
```
pip install gh-stars
```
and use the command-line tools as displayed. The `-h` switch gives more details.

## Gallery

A collection of the GitHub stars for of a number of topics.

#### Programming languages
![github-programming-languages](https://nschloe.github.io/gh-stars/github-programming-languages.svg)

#### Version control systems
![github-vcs](https://nschloe.github.io/gh-stars/github-version-control-systems.svg)

#### Frontend frameworks
![github-frontend-frameworks](https://nschloe.github.io/gh-stars/github-frontend-frameworks.svg)

#### Backend frameworks
![github-backend-frameworks](https://nschloe.github.io/gh-stars/github-backend-frameworks.svg)

#### Browsers
![github-browsers](https://nschloe.github.io/gh-stars/github-browsers.svg)

#### Databases
![github-databases](https://nschloe.github.io/gh-stars/github-databases.svg)

#### JavaScript
* Package managers
  ![github-javascript-package-managers](https://nschloe.github.io/gh-stars/github-javascript-package-managers.svg)
* Testing frameworks
  ![github-javascript-testing-frameworks](https://nschloe.github.io/gh-stars/github-javascript-testing-frameworks.svg)
* Popular packages
  ![github-popular-javascript](https://nschloe.github.io/gh-stars/github-popular-javascript.svg)

#### Text editors
![github-text-editors](https://nschloe.github.io/gh-stars/github-text-editors.svg)

#### Operating systems
![github-operating-systems](https://nschloe.github.io/gh-stars/github-operating-systems.svg)

#### Linux window managers
![github-linux-window-managers](https://nschloe.github.io/gh-stars/github-linux-window-managers.svg)

#### Code-hosting platforms
![github-code-hosting-platforms](https://nschloe.github.io/gh-stars/github-code-hosting-platforms.svg)

#### Content-management systems
![github-content-management-systems](https://nschloe.github.io/gh-stars/github-content-management-systems.svg)

#### Continuous-integration services
![github-continuous-integration-services](https://nschloe.github.io/gh-stars/github-continuous-integration-services.svg)

#### Office suites
![github-office-suites](https://nschloe.github.io/gh-stars/github-office-suites.svg)

#### Video editors
![github-video-editors](https://nschloe.github.io/gh-stars/github-video-editors.svg)

#### Computer algebra systems
![github-computer-algebra-systems](https://nschloe.github.io/gh-stars/github-computer-algebra-systems.svg)

#### DevOps
![github-devops](https://nschloe.github.io/gh-stars/github-devops.svg)

#### Build systems
![github-build-systems](https://nschloe.github.io/gh-stars/github-build-systems.svg)

#### Machine learning
![github-machine-learning](https://nschloe.github.io/gh-stars/github-machine-learning.svg)

#### Python
* Science
  ![github-scientific-python](https://nschloe.github.io/gh-stars/github-scientific-python.svg)

* Plotting
  ![github-python-plotting](https://nschloe.github.io/gh-stars/github-python-plotting.svg)

* Testing
  ![github-python-testing](https://nschloe.github.io/gh-stars/github-python-testing.svg)

* Static code analysis
  ![github-python-static-analysis](https://nschloe.github.io/gh-stars/github-python-static-analysis.svg)

#### Terminals
* Shells
  ![github-shells](https://nschloe.github.io/gh-stars/github-shells.svg)

* Terminal emulators
  ![github-linux-terminal-emulators](https://nschloe.github.io/gh-stars/github-linux-terminal-emulators.svg)

* Color schemes
  ![github-terminal-color-schemes](https://nschloe.github.io/gh-stars/github-terminal-color-schemes.svg)

* Monospaced fonts
  ![github-monospaced-fonts](https://nschloe.github.io/gh-stars/github-monospaced-fonts.svg)

#### vim
* vim variants
  ![github-vim-variants](https://nschloe.github.io/gh-stars/github-vim-variants.svg)

* Plug-in managers
  ![github-vim-plugin-managers](https://nschloe.github.io/gh-stars/github-vim-plugin-managers.svg)

* Plug-ins
  ![github-vim-plugins](https://nschloe.github.io/gh-stars/github-vim-plugins.svg)


#### Proofreading tools
  ![github-proofreading](https://nschloe.github.io/gh-stars/github-proofreading-tools.svg)

### Related projects

 * [star-history](https://github.com/timqian/star-history)
 * [star-history](https://github.com/dtolnay/star-history)

### License
This software is published under the [GPLv3 license](https://www.gnu.org/licenses/gpl-3.0.en.html).
