__author__ = 'Matt David'

from attrdict import AttrDict
from datetime import datetime, timedelta

from addressimo.config import config

# Used Datapoints:
#
# id
#
# bip70_static_amount
# bip70_enabled
# last_generated_index
# last_used_index
# master_public_key
# master_public_key_source
# private_key
# private_key_source
# private_key_id
# x509_cert
# x509_cert_source
# prr_only

class IdObject(AttrDict):

    def __init__(self, id=None):

        # Set ID
        self.id = id

        # Set Defaults
        self.bip32_enabled = False
        self.bip70_static_amount = None
        self.bip70_enabled = False
        self.prr_only = False
        self.wallet_address = None
        self.expires = 0
        self.memo = None
        self.master_public_key = None
        self.private_key = None
        self.x509_cert = None
        self.payment_url = None
        self.merchant_data = None
        self.presigned_payment_requests = []
        self.presigned_only = False
        self.auth_public_key = None

    def get_expires(self):
        if self.expires:
            if isinstance(self.expires, int) or isinstance(self.expires, long):
                return int((datetime.utcnow() + timedelta(seconds=self.expires)).strftime('%s'))
            elif isinstance(self.expires, datetime):
                return int(self.expires.strftime('%s'))
        else:
            return int((datetime.utcnow() + timedelta(seconds=config.bip70_default_expiration)).strftime('%s'))
