import simplejson as json
import logging

__all__ = ['TW_ACTIONS', 'TWRequest']

DELIMETER = '\n'

class TW_ACTIONS: # действия для TW_UPDATE
    LOCATE = 0
    REMOVE = 1


class TW_API: # нравятся jsonчики
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
    def __init__(self, sock):
        self.logger = logging.getLogger(__name__)
        self.__storage = []
        self.sock = sock


    def api_init(self, nlvl=None): # каждый json в TW_API имеет свой метод, которым он конструируется и отправляется
        self._request(TW_API.INIT, nlvl=nlvl)


    def api_key(self, key, keytype):
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
        self.logger.debug('SEND: {}'.format(data))
        self.sock.send((json.dumps(data)+DELIMETER).encode('utf-8'))


    def _receive(self):
        if len(self.__storage):
            try:
                return json.loads(self.__storage.pop())
            except json.JSONDecodeError:
                return None
        data = self.sock.recv(1024).decode('utf-8').split(DELIMETER) # замечал, что на сокет изредка приходят куски чужих данных, поэтому приходится разделять
        data.pop()
        if len(data) > 1:
            self.__storage.extend(data[1:]) # прилетевшие не вовремя куски сохраняем в кэше, дабы другому клиенту не пришлось переспрашивать
        try:
            self.logger.debug('RECV: {}'.format(data[0]))
            return json.loads(data[0])
        except:
            return None
