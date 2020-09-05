import base64
import ConfigParser
import datetime
try:
    import json
except:
    import simplejson as json
import sqlite3
import urllib2

def get_reviewers():
    reviewers_conf = "https://raw.githubusercontent.com/servo/saltfs/master/homu/files/cfg.toml"
    f = urllib2.urlopen(reviewers_conf)
    contents = f.read()
    start_str = "{% set reviewers = ["
    start = contents.find(start_str)
    assert start != -1
    start += len(start_str)
    end = contents.find("] %}", start + 1)
    assert end != -1

    reviewers = []
    reviewers_raw = contents[start:end].split('\n')
    for reviewer in reviewers_raw:
        if reviewer:
            # |    "jdm",|
            reviewers += [reviewer.strip()[1:-2]]
    return reviewers

def scrape_into_db():
    reviewers = get_reviewers()

    config = ConfigParser.RawConfigParser()
    config.read('./config')
    user = config.get('github', 'user')
    token = config.get('github', 'token')

    queue_url = "https://api.github.com/repos/servo/servo/issues?assignee={0}&labels=S-awaiting-review"
    to_insert = []
    today = datetime.datetime.today()

    for reviewer in reviewers:
        print("Processing %s" % reviewer)
        req = urllib2.Request(queue_url.format(reviewer), headers={
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': 'Basic ' + base64.standard_b64encode('%s:%s' % (user, token)).replace('\n', ''),
        })
        reviews = urllib2.urlopen(req)
        data = json.loads(reviews.read())
        queue_size = len(data)
        average_age = 0
        oldest = None
        for review in data:
            age = (today - datetime.datetime.strptime(review['created_at'], "%Y-%m-%dT%H:%M:%SZ")).days
            average_age += age
            if not oldest or age > oldest:
                oldest = age

        if not queue_size:
            oldest = 0
        else:
            average_age /= queue_size

        to_insert += [(reviewer, today.isoformat(), queue_size, average_age, oldest)]

    conn = sqlite3.connect('queues.db')
    c = conn.cursor()
    c.executemany('INSERT INTO queues VALUES (?,?,?,?,?)', to_insert)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    scrape_into_db()
