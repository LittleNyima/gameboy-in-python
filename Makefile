.PHONY : clean
clean:
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/

.PHONY : publish
publish: clean
	python -m pip install .
	python setup.py sdist bdist_wheel
	ls dist
	twine upload dist/*
