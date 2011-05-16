from google.appengine.ext import db

def key(*args):
    return db.Key.from_path(*args).id_or_name()

def get_or_create(model, **kwargs):
    key_name = key(model.kind(), '/'.join(kwargs.values()))
    return model.get_or_insert(key_name, **kwargs)

def parse_timestamp(timestamp):
    FORMAT = '%Y-%m-%dT%H:%M:%S'
    if '.' in timestamp:
        nofrag, frag = timestamp.split('.')
        nofrag_dt = datetime.strptime(nofrag, FORMAT)
        dt = nofrag_dt.replace(microsecond=int(frag))
        return dt
    else:
        return datetime.strptime(timestamp, FORMAT)

