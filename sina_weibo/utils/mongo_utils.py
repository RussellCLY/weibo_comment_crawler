import pymongo


def mongo_conn(user_name=None, password=None, host="localhost:27017", database_name='', is_settings=True):
    """
    MongoDB链接
    @param user_name:
    @param password:
    @param host:
    @param database_name:
    @param is_settings:
    @return:
    """
    if user_name and password and database_name:
        mongo_uri = "mongodb://" + user_name + ":" + password + "@" + host + "/" + database_name
    elif is_settings:
        mongo_uri = "mongodb://" + host + "/" + database_name
    else:
        mongo_uri = "mongodb://" + host

    return pymongo.MongoClient(mongo_uri, connect=False)


if __name__ == '__main__':
    pass
