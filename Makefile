lastbart: bart.sqlite
	mkdir -p html
	python3 lastbart.py

bart.sqlite: google_transit.zip
	gtfsdb-load --database_url sqlite:///bart.sqlite google_transit.zip

google_transit.zip:
	wget -N https://bart.gov/dev/schedules/google_transit.zip

serve:
	python3 -m http.server --bind 127.0.0.1 --directory html

clean:
	rm -f google_transit.zip
	rm -f bart.sqlite
	rm -rf html
