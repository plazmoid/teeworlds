from functools import partial
import simplejson as json
import logging

__all__ = ['TW_ACTIONS', 'TWRequest']

class TW_ACTIONS:
    LOCATE = 0
    REMOVE = 1


class TW_API:
    """
    Possible API methods
    """
    
    @staticmethod
    def INIT(**kwargs):
        return {'session': kwargs['session'],
                'method': 'INIT',
                'nlvl': kwargs['nlvl']}

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
        self.logger = logging.getLogger(__name__)
        self.sock = sock
        self.session = session if session else None
        self.__storage = []

    def api_init(self, nlvl=None):
        self._request(TW_API.INIT, nlvl=nlvl)

    def api_key(self, key, keytype):
        self._request(TW_API.KEY, key=key, keytype=keytype)

    def api_close(self):
        self._request(TW_API.CLOSE)

    def api_update(self, entity=None, action=None, params=None, constructOnly=False):
        updated = None
        if entity:
            if type(entity) == int: #update a single entity
                updated = TW_API.UPD_PARAMS(uid=entity, action=action, params=params)
            elif type(entity) == list: #update all
                updated = [TW_API.UPD_PARAMS(uid=k.session, action=action, params=getattr(v, params)()) for k, v in entity]
            else:
                self.logger.warn('Invalid entity type: ' + str(entity))
        if constructOnly:
            return partial(self._request, TW_API.UPDATE, updated=updated)
        self._request(TW_API.UPDATE, updated=updated)

    def _request(self, method, **kwargs):
        data = method(session=self.session, **kwargs)
        self.logger.debug('SEND: {}'.format(data))
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
        self.logger.debug('RECV: {}'.format(data[0]))
        try:
            return json.loads(data[0])
        except:
            return None
        
