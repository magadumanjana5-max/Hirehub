from pymongo import MongoClient


def init_mongodb(app):
    if app.config.get('USE_IN_MEMORY_DB'):
        app.config['DATA_STORE'] = app.config.get('DATA_STORE', {})
        return

    client = MongoClient(
        app.config['MONGODB_URI'],
        serverSelectionTimeoutMS=app.config['MONGODB_SERVER_SELECTION_TIMEOUT_MS'],
    )
    client.admin.command('ping')
    app.config['MONGO_CLIENT'] = client
    app.config['MONGO_DB'] = client[app.config['MONGODB_DATABASE']]
    app.config['MONGO_DB']['users'].create_index('email', unique=True)
    app.config['MONGO_DB']['applications'].create_index(
        [('candidate_id', 1), ('job_id', 1)],
        unique=True,
    )
    app.config['MONGO_DB']['applications'].create_index([('job_id', 1), ('status', 1)])
    app.config['MONGO_DB']['notifications'].create_index([('user_id', 1), ('is_read', 1)])
    app.config['MONGO_DB']['interviews'].create_index([('candidate_id', 1), ('scheduled_at', 1)])


def close_mongodb(app):
    client = app.config.get('MONGO_CLIENT')
    if client is not None:
        client.close()
