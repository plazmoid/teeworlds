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
        data = method(session=self.session, **kwargs)
        self.sock.send(json.dumps(data).encode('utf-8'))

    def _receive(self):
        data = self.sock.recv(1024).decode('utf-8')
        return json.loads(data)
        
