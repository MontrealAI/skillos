.PHONY: demo serve test pages clean

demo:
	python -m skillos.cli demo

serve:
	python -m skillos.cli serve

test:
	python -m unittest discover -s tests -v

pages:
	python scripts/build_pages.py

clean:
	rm -rf .skillos dist build *.egg-info
