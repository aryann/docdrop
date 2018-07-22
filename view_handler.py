import httplib
import logging
import mimetypes

from google.appengine.ext import ndb
import webapp2

import models


class ViewHandler(webapp2.RequestHandler):

    def get(self):
        logging.info('hello')
    
    def get(self, id):
        key = ndb.Key(models.File, id)
        file_entity = key.get()
        
        if not file_entity:
            self.error(httplib.NOT_FOUND)
            return
        
        content_type, _ = mimetypes.guess_type(file_entity.filename)

        # Add 'Content-Disposition: attachment; filename="X"' to force
        # download.
        self.response.headers['Content-Type'] = content_type
        self.response.write(file_entity.payload)
        

app = webapp2.WSGIApplication([
    webapp2.Route('/view/<id>', ViewHandler),
], debug=False)
