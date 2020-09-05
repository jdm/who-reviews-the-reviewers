import datetime
import sqlite3
import scrape

reviewers = scrape.get_reviewers()

conn = sqlite3.connect('queues.db')
c = conn.cursor()

with open('entry.html') as f:
    entry = f.read()    

with open('data.html') as f:
    script = f.read()

with open('data.json') as f:
    data = f.read()

body = []
scripts = []
for reviewer in reviewers:
    result = c.execute('SELECT * FROM queues WHERE name=? ORDER BY date', (reviewer,))
    queue_sizes = []
    averages = []
    oldest = []
    dates = []

    for row in result:
        queue_sizes += [int(row[2])]
        averages += [float(row[3])]
        oldest += [int(row[4])]
        dates += [datetime.datetime.strptime(row[1], "%Y-%m-%dT%H:%M:%S.%f")]

    classname = 'empty' if not queue_sizes[-1] else ''
    body += [entry.format(name=reviewer,
                          queue=queue_sizes[-1],
                          oldest=oldest[-1],
                          average=averages[-1],
                          empty=classname)]
    
    all_points = []
    points = ["{{ x: new Date({year},{month},{day}), y: {size} }}".format(year=d.year,
                                                                          month=d.month-1,
                                                                          day=d.day,
                                                                          size=s)
               for (d, s) in zip(dates, queue_sizes)[-14:]]
    all_points += [data.format(points=',\n'.join(points),
                               axis='primary',
                               legend='PRs in queue')]

    points = ["{{ x: new Date({year},{month},{day}), y: {oldest} }}".format(year=d.year,
                                                                            month=d.month-1,
                                                                            day=d.day,
                                                                            oldest=o)
              for (d, o) in zip(dates, oldest)[-14:]]
    all_points += [data.format(points=',\n'.join(points),
                               axis='secondary',
                               legend='Oldest PR')]

    points = ["{{ x: new Date({year},{month},{day}), y: {average} }}".format(year=d.year,
                                                                             month=d.month-1,
                                                                             day=d.day,
                                                                             average=a)
              for (d, a) in zip(dates, averages)[-14:]]
    all_points += [data.format(points=',\n'.join(points),
                               axis='secondary',
                               legend='Rolling average PR age')]

    scripts += [script.format(name=reviewer,
                              data=',\n'.join(all_points))]

conn.close()

with open('template.html') as f:
    template = f.read()

print(template.format(entries='\n'.join(body),
                      scripts='\n'.join(scripts)))
