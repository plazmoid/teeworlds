from random import randint
import pickle
import logging


__all__ = ['TW_ACTIONS', 'TWRequest']


class TW_ACTIONS: # действия для TW_UPDATE
    LOCATE = 0
    REMOVE = 1
    SWITCH = 2


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
    def UPD_DATA(**kwargs): # используется совместно с методом UPDATE, собирается в список и передаётся в кварг 'updated'
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
        
    @staticmethod
    def INTERACT(**kwargs): # взаимодействия игроков с окружающим миром
        return {'uid': kwargs['uid'],
                'method': 'INTERACT',
                'target': kwargs['target']}

        

class TWRequest: # шаблоны общения клиента и сервера
    """
    Serialize data to bytes and construct/validate a request
    """
    def __init__(self, sock, client=False):
        self.logger = logging.getLogger(__name__)
        self.sock = sock
        self.client = client
        self.last_pid = None


    def api_init(self, nlvl=None): # каждый json в TW_API имеет свой метод, которым он конструируется и отправляется
        self._request(TW_API.INIT, nlvl=nlvl)


    def api_key(self, keytype, key=None):
        self._request(TW_API.KEY, key=key, keytype=keytype)


    def api_close(self):
        self._request(TW_API.CLOSE)
        
        
    def api_ping(self):
        self._request(TW_API.PING)


    def api_interact(self, target):
        self._request(TW_API.INTERACT, target=target)
        

    def api_update(self, entity=None, action=None, params=None):
        def getparams(obj):
            return getattr(obj, params)() if params else None
        
        if entity: # обновлять можно
            if type(entity) == list: # списком
                updated = [TW_API.UPD_DATA(uid=e.uid, action=action, params=getparams(e)) for e in entity]
            elif type(entity) == int: # по uid'у
                updated = [TW_API.UPD_DATA(uid=entity, action=action, params=None)]
            else: # по сущности TWObject
                updated = [TW_API.UPD_DATA(uid=entity.uid, action=action, params=getparams(entity))]
        self._request(TW_API.UPDATE, updated=updated)


    def _request(self, method, **kwargs):
        try:
            uid = self.player.uid
        except AttributeError:
            uid = -1
        data = method(uid=uid, **kwargs) # в каждый реквест зашивается uid отправителя (кроме запроса на инициализацию)
        if self.client:
            self.last_pid = randint(0, 65535)
        data['pid'] = self.last_pid
        self.logger.debug('SEND: {}'.format(data))
        data = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        self.sock.send(len(data).to_bytes(2, 'big') + data)


    def _receive(self):
        datalen = int.from_bytes(self.sock.recv(2), 'big')
        data = self.sock.recv(datalen)
        try:
            data = pickle.loads(data)
            if self.client:
                if self.last_pid == data['pid']:
                    self.last_pid = data['pid']
                    self.logger.debug('RECV: {}'.format(data))
                    return data
            else:
                self.last_pid = data['pid']
                self.logger.debug('RECV: {}'.format(data))
                return data
        except:
            return None
            
    
