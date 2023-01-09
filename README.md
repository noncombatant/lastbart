# lastbart

A simple web site to show the last departure times per day for Bay Area Rapid
Transit (BART) stops.

Using Python, lastbart generates static HTML files that you can serve from any
web server.

## Installation

These steps assume a Debian- or Ubuntu-like Linux system — anything with `apt`.
On other systems, there will likely be a similar package manager that works in a
similar way.

Install Python 3 and the Python libraries we need:

```bash
$ sudo apt install python3-pip
$ pip3 install --user pystache
$ pip3 install --user gtfsdb
```

Then download lastbart and build the HTML files:

```bash
$ git clone https://github.com/jsha/lastbart
$ cd lastbart
$ PATH="$HOME/.local/bin:$PATH" make
```

To view the output, you can load them as files in your browser:

```bash
$ firefox html/index.html
```

or serve them with Python’s simple HTTP server:

```bash
$ PATH="$HOME/.local/bin:$PATH" make serve
$ firefox http://127.0.0.1:8000/
```
