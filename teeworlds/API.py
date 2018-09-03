import simplejson as json
import logging

__all__ = ['TW_ACTIONS', 'TW_API', 'TWRequest']

class TW_ACTIONS:
    LOCATION = 0
    REMOVE = 1


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
    def UPD_PARAMS(**kwargs):
        return {'uid': kwargs['uid'],
                'action': kwargs['action'],
                'params': kwargs['params']}
        
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
        
    @staticmethod
    def CLOSE(**kwargs):
        return {'session': kwargs['session'],
                'method': 'CLOSE'}


class TWRequest:
    """
    Serialize data to bytes and construct/validate a request
    """
    def __init__(self, sock, session=None):
        logging.basicConfig(level=logging.WARN)
        self.logger = logging.getLogger(__name__)
        self.sock = sock
        self.session = session if session else ''
        self.__storage = []

    def _request(self, method, **kwargs):
        data = method(session=self.session, **kwargs)
        self.logger.info('SEND: {}'.format(data))
        self.sock.send((json.dumps(data)+'\n').encode('utf-8'))

    def _receive(self):
        if len(self.__storage):
            #self.logger.info('STORAGE: {}'.format(self.__storage))
            try:
                return json.loads(self.__storage.pop())
            except json.JSONDecodeError:
                return None
        data = self.sock.recv(1024).decode('utf-8').split('\n')
        data.pop()
        if len(data) > 1:
            self.__storage.extend(data[1:])
        self.logger.info('RECV: {}'.format(data))
        return json.loads(data[0])
        
