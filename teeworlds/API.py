import simplejson as json

class TW_API:
    """
    Possible API methods
    """
    @staticmethod
    def INIT(**kwargs):
        return {'session': kwargs['session'],
                'method': 'INIT'}

    @staticmethod
    def UPDATE(**kwargs):
        return {'session': kwargs['session'],
                'method': 'UPDATE',
                'updated': kwargs['updated']}
        
    @staticmethod
    def KEY(**kwargs):
        return {'session': kwargs['session'],
                'method': 'KEY',
                'key': kwargs['key'],
                'keytype': kwargs['keytype']}
        
    @staticmethod
    def ERR(**kwargs):
        return {'session': kwargs['session'],
                'method': 'ERR',
                'code': kwargs['code']}


class TWRequest:
    """
    Serialize data to bytes and construct/validate a request
    """
    def __init__(self, sock, session=None):
        self.sock = sock
        self.session = session if session else ''

    def _request(self, method, **kwargs):
        self.sock.send(json.dumps(method(session=self.session, **kwargs)))

    def _receive(self):
        data, addr = self.sock.recv(1024)
        return (json.loads(data), addr)
        
