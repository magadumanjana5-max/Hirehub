from __future__ import annotations
import uuid

from flask import current_app
from pymongo import ReturnDocument


class BaseRepository:
    collection_name = 'records'

    def __init__(self):
        self.database = current_app.config.get('MONGO_DB')
        if self.database is None and not current_app.config.get('USE_IN_MEMORY_DB'):
            raise RuntimeError('MongoDB is not initialized for this application')
        self.store = current_app.config.get('DATA_STORE', {
            'users': [],
            'companies': [],
            'jobs': [],
            'applications': [],
            'interviews': [],
            'notifications': [],
            'resumes': [],
        })

    def _collection(self):
        if self.database is not None:
            return self.database[self.collection_name]
        return self.store.setdefault(self.collection_name, [])

    def all(self):
        collection = self._collection()
        if self.database is not None:
            return [self._without_mongo_id(item) for item in collection.find()]
        return list(collection)

    def get_by_id(self, record_id):
        collection = self._collection()
        if self.database is not None:
            item = collection.find_one({'id': record_id})
            return self._without_mongo_id(item) if item else None
        for item in collection:
            if item.get('id') == record_id:
                return item
        return None

    def create(self, payload):
        payload = dict(payload)
        if 'id' not in payload:
            payload['id'] = str(uuid.uuid4())
        collection = self._collection()
        if self.database is not None:
            collection.insert_one(payload)
        else:
            collection.append(payload)
        return payload

    def update(self, record_id, payload):
        collection = self._collection()
        if self.database is not None:
            item = collection.find_one_and_update(
                {'id': record_id},
                {'$set': payload},
                return_document=ReturnDocument.AFTER,
            )
            return self._without_mongo_id(item) if item else None
        for index, item in enumerate(collection):
            if item.get('id') == record_id:
                collection[index].update(payload)
                return collection[index]
        return None

    def delete(self, record_id):
        collection = self._collection()
        if self.database is not None:
            item = collection.find_one_and_delete({'id': record_id})
            return self._without_mongo_id(item) if item else None
        for index, item in enumerate(collection):
            if item.get('id') == record_id:
                return collection.pop(index)
        return None

    @staticmethod
    def _without_mongo_id(item):
        if item is None:
            return None
        item.pop('_id', None)
        return item
