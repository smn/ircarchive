import sys, random
from datetime import datetime, timedelta

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

json = """{
 "nickname": "%(nickname)s",
 "server": "irc.freenode.net",
 "channel": "#vumi",
 "message_type": "message",
 "message_content": "testing app engine at %(date)s",
 "timestamp": "%(date)s"
}""".replace('\n', '')

if len(sys.argv) == 1:
    print 'Usage: python create-sample-content.py <records> [seconds|minutes|hours|days]'
    sys.exit(1)

limit = int(sys.argv[1]) if len(sys.argv) > 1 else 100
interval = sys.argv[2] if len(sys.argv) > 2 else "minutes"

for i in range(0, limit):
    timestamp = datetime.utcnow() - timedelta(**{interval: i})
    payload = json % {
        'date': timestamp.strftime(DATE_FORMAT),
        'nickname': random.sample(['foo', 'bar', 'boo', 'far', 'baz'], 1).pop()
    }
    print "curl -X POST http://localhost:8080/ -d '%s'" % payload
