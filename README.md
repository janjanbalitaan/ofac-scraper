# ofac-scraper

# Requirements
1. Python 3
2. Virtualenvironment

# Description
Ofac scraper was used to extract data of the people who are included in the sanctions list in https://sanctionssearch.ofac.treas.gov/. This will also help financial technology applications or systems to monitor their transactions on the extracted list.

# How to use
* ofac search per country will be run using
$ python ofac-scraper-per-country.py "China"

* ofac search will be automatically generate all the countries avaialbe
$ python ofac-scraper.py
