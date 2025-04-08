on dev branch commit (using commitizen):
	precommit, also make it check commit is valid for commitizen
	then actions lint

experimental releases(manually triggered workflow, where alpha, beta, etc... is specified):
	precommit, also make it check commit is valid for commitizen
	github pages
	then actions lint
	make builds for pypi
	publish to pypi under pre-release
	make builds for github releases
	publish to github as pre-release

on dev merge to main:
	precommit, also make it check commit is valid for commitizen
	then actions lint
	github pages
	make builds for pypi
	publish to pypi as latest
	make builds for github releases
	publish to github as latest
