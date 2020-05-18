from app import current_app
import datetime as dt
import json


class RedisRegistry:
    def __init__(self, Obj):
        self.obj = Obj

    def save(self):
        current_app.logger.debug(self.obj.__dict__())
        for key, value in self.obj.__dict__().items():
            value['class'] = self.obj.__class__.__name__
            jsonify_dict = {key: json.dumps(value)}
            current_app.redis.mset(jsonify_dict)
            current_app.logger.debug(jsonify_dict)
        current_app.redis.expire(self.obj.obj_id, dt.timedelta(hours=self.obj.ttl))

    def destroy(self):
        try:
            current_app.redis.delete(self.obj.obj_id)
        except Exception as e:
            current_app.logger.error(e)
            return False
        return True

    @classmethod
    def load(cls, obj_id: str, class_reference):
        obj = current_app.redis.get(obj_id)
        if obj:
            current_app.logger.debug('Loaded from redis:' + obj.decode("UTF-8"))
            obj = json.loads(obj)
            if obj['class'] == class_reference.__name__:
                current_app.logger.debug('Loaded from redis:' + str(obj))
                return class_reference(obj, obj_id=obj_id, from_db=True)
        current_app.logger.debug('Object <{}> of class {}, not found in redis'.format(obj_id,
                                                                                      class_reference.__name__))
        return None
