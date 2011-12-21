lastbart:
	python lastbart.py

bart.sqlite: google_transit.zip
	gtfsdb-load --database_url sqlite:///bart.sqlite google_transit.zip

google_transit.zip:
	wget -N http://bart.gov/dev/schedules/google_transit.zip
