from random import randint
import pickle
import logging


__all__ = ['TW_ACTIONS', 'TWRequest']


class TW_ACTIONS: # действия для TW_UPDATE
    LOCATE = 0
    REMOVE = 1
    SHOOT = 2
    HOOK = 3


class TW_API:
    """
    Possible API methods
    """
    
    @staticmethod
    def INIT(**kwargs):
        return {'uid': kwargs['uid'],
                'method': 'INIT',
                'nlvl': kwargs['nlvl'],
                'color': kwargs['color']}

    @staticmethod
    def UPDATE(**kwargs):
        return {'uid': kwargs['uid'],
                'method': 'UPDATE',
                'updated': kwargs['updated']}
        
    @staticmethod
    def UPD_ITEM(**kwargs): # используется совместно с методом UPDATE, собирается в список и передаётся в кварг 'updated'
        return {'uid': kwargs['uid'],
                'action': kwargs['action'],
                'attrib': kwargs['attrib']}
        
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
        

    def api_update(self, entity=None, action=None, attrib=None, upd_pid=True):
        def getattrib(obj):
            attr = getattr(obj, attrib) if attrib else None    
            return attr() if callable(attr) else attr
        
        if entity: # обновлять можно
            if type(entity) == list: # списком
                updated = [TW_API.UPD_ITEM(uid=e.uid, action=action, attrib=getattrib(e)) for e in entity]
            elif type(entity) == int: # по uid'у
                updated = [TW_API.UPD_ITEM(uid=entity, action=action, attrib=attrib)]
            else: # по сущности TWObject
                updated = [TW_API.UPD_ITEM(uid=entity.uid, action=action, attrib=getattrib(entity))]
        self._request(TW_API.UPDATE, updated=updated, upd_pid=upd_pid)


    def _request(self, method, **kwargs):
        try:
            uid = self.player.uid
        except AttributeError:
            uid = -1
        data = method(uid=uid, **kwargs) # в каждый реквест зашивается uid отправителя (кроме запроса на инициализацию)
        if self.client and 'upd_pid' in kwargs and kwargs['upd_pid']:
            self.last_pid = randint(0, 65535) # каждый реквест имеет свой pid, на который сервер должен ответить
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
                if self.last_pid == data['pid']: # компенсация лагов, клиент реагирует только на самый последний ответ сервера
                    self.logger.debug('RECV: {}'.format(data))
                    return data
            else:
                self.last_pid = data['pid']
                self.logger.debug('RECV: {}'.format(data))
                return data
        except:
            return None
            
    
