from functools import partial
import simplejson as json
import logging

__all__ = ['TW_ACTIONS', 'TWRequest']

DELIMETER = '\n'

class TW_ACTIONS:
    LOCATE = 0
    REMOVE = 1


class TW_API:
    """
    Possible API methods
    """
    
    @staticmethod
    def INIT(**kwargs):
        return {'uid': kwargs['uid'],
                'method': 'INIT',
                'nlvl': kwargs['nlvl']}

    @staticmethod
    def UPDATE(**kwargs):
        return {'uid': kwargs['uid'],
                'method': 'UPDATE',
                'updated': kwargs['updated']}
        
    @staticmethod
    def UPD_PARAMS(**kwargs):
        return {'uid': kwargs['uid'],
                'action': kwargs['action'],
                'params': kwargs['params']}
        
    @staticmethod
    def KEY(**kwargs):
        return {'uid': kwargs['uid'],
                'method': 'KEY',
                'key': kwargs['key'],
                'keytype': kwargs['keytype']}
        
    @staticmethod
    def ERR(**kwargs):
        return {'uid': kwargs['uid'],
                'method': 'ERR',
                'code': kwargs['code']}
        
    @staticmethod
    def CLOSE(**kwargs):
        return {'uid': kwargs['uid'],
                'method': 'CLOSE'}

    @staticmethod
    def PING(**kwargs):
        return {'uid': kwargs['uid'],
                'method': 'PING'}
        

class TWRequest:
    """
    Serialize data to bytes and construct/validate a request
    """
    def __init__(self, sock):
        self.logger = logging.getLogger(__name__)
        self.__storage = []
        self.sock = sock
        self.sock.setblocking(True)


    def api_init(self, nlvl=None):
        self._request(TW_API.INIT, nlvl=nlvl)


    def api_key(self, key, keytype):
        self._request(TW_API.KEY, key=key, keytype=keytype)


    def api_close(self):
        self._request(TW_API.CLOSE)
        
        
    def api_ping(self):
        self._request(TW_API.PING)


    def api_update(self, entity=None, action=None, params=None, constructOnly=False):
        def getparams(obj):
            return getattr(obj, params)() if params else None
        
        if entity:
            if type(entity) == list: #update all
                updated = [TW_API.UPD_PARAMS(uid=e.uid, action=action, params=getparams(e)) for e in entity]
            else: #update a single entity
                updated = [TW_API.UPD_PARAMS(uid=entity.uid, action=action, params=getparams(entity))]
        if constructOnly:
            return partial(self._request, TW_API.UPDATE, updated=updated)
        self._request(TW_API.UPDATE, updated=updated)


    def _request(self, method, **kwargs):
        try:
            uid = self.player.uid
        except AttributeError:
            uid = -1
        data = method(uid=uid, **kwargs)
        self.logger.debug('SEND: {}'.format(data))
        self.sock.send((json.dumps(data)+DELIMETER).encode('utf-8'))


    def _receive(self):
        if len(self.__storage):
            try:
                return json.loads(self.__storage.pop())
            except json.JSONDecodeError:
                return None
        data = self.sock.recv(1024).decode('utf-8').split(DELIMETER)
        data.pop()
        if len(data) > 1:
            self.__storage.extend(data[1:])
        try:
            self.logger.debug('RECV: {}'.format(data[0]))
            return json.loads(data[0])
        except:
            return None
