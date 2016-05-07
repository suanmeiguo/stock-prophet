DATE = `date +%F`

download:
	python download.py

run:
	python main.py > $(DATE).csv
