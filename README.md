# lastbart

A simple web site to show the last departure times per day for Bay Area Rapid
Transit (BART) stops.

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

Then download and build lastbart:

```bash
$ git clone https://github.com/jsha/lastbart
$ cd lastbart
$ PATH=~/.local/bin:$PATH make
$ firefox ./html/index.html
```
