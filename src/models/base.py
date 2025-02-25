from peewee import Model
from .database import db


class BaseModel(Model):

    @classmethod
    def update_or_create(cls, **kwargs):
        defaults = kwargs.pop('defaults', {})
        entity: Model
        entity, created = cls.get_or_create(**kwargs)
        if not created:
            for key, value in defaults.items():
                setattr(entity, key, value)
            entity.save()
        return entity, created

    class Meta:
        database = db
