from google.appengine.ext import ndb


class Users(ndb.Model):
    email = ndb.StringProperty(required=True)


class File(ndb.Model):
    user_email = ndb.StringProperty(required=True)
    filename = ndb.StringProperty(required=True)
    payload = ndb.BlobProperty(required=True, indexed=False)
    created = ndb.DateTimeProperty(auto_now_add=True)
