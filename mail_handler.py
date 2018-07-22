import httplib
import logging
import random
import re
import string

from google.appengine.api import app_identity
from google.appengine.api import mail
from google.appengine.ext import ndb
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import webapp2

import models

MAIL_SENDER = 'confirmations@docdrop651.appspotmail.com'

def _generate_id():
    return ''.join(random.choice(string.ascii_lowercase) for _ in xrange(6))


class EmailHandler(InboundMailHandler):

    def receive(self, incoming_message):
        sender_email = re.search('.*<(.*)>', incoming_message.sender)
        if not sender_email:
            self.error(httplib.BAD_REQUEST)
            logging.error('Could not extract email from: %s',
                          incoming_message.sender)
            return
        sender_email = sender_email.group(1)
        
        file_entities = []        
        for attachment in getattr(incoming_message, 'attachments', []):
            file_entities.append(models.File(
                id=_generate_id(),
                user_email=sender_email,
                filename=attachment.filename,
                payload=attachment.payload.decode()))

        if not file_entities:
            logging.info('Email from %s contained no attachments.',
                         sender_email)
            outgoing_message = mail.EmailMessage(
                sender=MAIL_SENDER,
                to=sender_email,
                subject="You didn't send us any files.",
                body=('You asked us to save some files for you, '
                      'but you did not attach any in your email.'))
            outgoing_message.send()
            return

        ndb.put_multi(file_entities)
        logging.info('Saved %d file(s) for %s.',
                     len(file_entities), sender_email)

        file_names = [entity.filename for entity in file_entities]
        file_urls = ['  * {}: {}/view/{}'.format(
            entity.filename,
            app_identity.get_default_version_hostname(),
            entity.key.id())
                     for entity in file_entities]
        
        outgoing_message = mail.EmailMessage(
            sender=MAIL_SENDER,
            to=sender_email,
            subject='We received your files: {}'.format(', '.join(file_names)),
            body='You can access them at the following locations:\n\n{}'.format(
                '\n'.join(file_urls)))
        outgoing_message.send()


app = webapp2.WSGIApplication([
    EmailHandler.mapping(),
], debug=False)
