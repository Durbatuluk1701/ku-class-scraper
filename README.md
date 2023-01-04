# KU Class Scraper

I created this tool to help efficiently look through and archive KU class data.

I grew tired of having to launch multiple queries on [classes.ku.edu](https://classes.ku.edu)
so this tool collects information over multiple semesters and years

Future Features:

- Display tool
- Stable query interface
- Data insights (when was a certain class last offered, what's changed, etc.)

Feel free to contribute

## Scrapy.py Usage

```
usage: scrapy.py [-h] department output start_year start_term end_year end_term

KU class info site scrapper

positional arguments:
department  = department code (EECS, CLSX, ...) to look search for
output      = file to output results to
start_year  = Start year
start_term  = Start term
end_year    = End year
end_term    = End term

options:
-h, --help show this help message and exit
```

### Examples

`python scrapy.py PHSX .\data\PHSX.json 2021 spring 2023 spring`
