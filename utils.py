from google.appengine.ext import db
from datetime import datetime

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

def parse_vumi_timestamp(timestamp):
    VUMI_DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
    return datetime.strptime(timestamp, VUMI_DATE_FORMAT)

# http://blog.notdot.net/2010/01/ReferenceProperty-prefetching-in-App-Engine
def prefetch_refprops(entities, *props):
    fields = [(entity, prop) for entity in entities for prop in props]
    ref_keys = [prop.get_value_for_datastore(x) for x, prop in fields]
    ref_entities = dict((x.key(), x) for x in db.get(set(ref_keys)))
    for (entity, prop), ref_key in zip(fields, ref_keys):
        prop.__set__(entity, ref_entities[ref_key])
    return entities

