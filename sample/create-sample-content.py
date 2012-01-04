import sys, random
from datetime import datetime, timedelta

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'


json = """{
    "to_addr": "%(nickname1)s!irc.freenode.net",
    "from_addr": "%(nickname2)s!irc.freenode.net",
    "content": "testing app engine at %(date)s",
    "transport_name": "irc_transport",
    "transport_type": "irc",
    "helper_metadata": {
        "irc": {
            "transport_nickname": "bot",
            "addressed_to_transport": false,
            "irc_server": "irc.freenode.net:6667",
            "irc_channel": "#vumi",
            "irc_command": "PRIVMSG"
        }
    }
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
        'nickname1': random.sample(['foo', 'bar', 'boo', 'far', 'baz'], 1).pop(),
        'nickname2': random.sample(['foo', 'bar', 'boo', 'far', 'baz'], 1).pop(),
    }
    print "curl -X POST http://localhost:8080/ -d '%s'" % payload
