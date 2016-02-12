Servo review queue overview
===========================

This tool is designed for two purposes:
* an overview of the state of the review queues of Servo's reviewers
* a historical record of the trends in review queues

What it measures
================

Based on the list of reviewers in the Homu configuration file:
* The number of PRs assigned to a particular github username at a given moment
* The number of days since the oldest assigned PR was created
* The average number of days since each assigned PR was created

These measurements are intended to reflect trends in reviewing. If a reviewer
consistently has a large queue size but the average age is very small, that
means they are being efficient in their reviews and no PR is lingering. On the
other hand, if the queue size fluctuates but the oldest PR age remains constant,
that means that a PR is being ignored.

It is unclear how meaningful average PR age is, but its intent is to indicate
something about how long PRs linger in a particular reviewer's queue.

How it works
============

```
$ sqlite3 queues.db <schema.sql
$ python scrape.py
$ python generate.py >index.html
```

scrape.py is intended to be run once per day to populate queues.db with
that day's data scraped from github's APIs. Any missed day will result in
missing data that cannot be recovered or synthesized.

generate.py uses the data in queues.db to fill out the various template
HTML files and generate the static page that contains the massaged and
charted data.
