from utils import getvalue

class Client(object):
    def __init__(self, db_config, models):
        self.db_config = db_config
        self.models = models

    def create_db(self, db_name):
        pass

    def delete_db(self, db_name):
        pass

    def db_exists(self, db_name):
        return True

    def setup(self, db_name):
        """
        Run when client connection is requested
        """
        pass

    def create(self, model, object):
        """

        :param params:
        :param kwargs:
        :return: object The object which was successfully created
        """

        raise NotImplementedError('You must implement a create func in your connection class')


    def list(self, model, filters, paginator=None, order_by=None, distinct=None,
             out_cols=None):
        raise NotImplementedError('You have not implemented a list func in your client class')

    def delete(self, model, id):
        raise NotImplementedError('You have not implemented a delete func in your client class')

    def update(self, model, id, update_with):
        raise NotImplementedError('You have not implemented an update func in your client class')

    def count(self, model, filters, distinct=None):
        raise NotImplementedError('You have not implemented a count function in your client class')

    def get_pks(self, model, filters):
        raise NotImplementedError("You have not implemented a get_pks function in your client class")

    def create_table(self, *args):
        pass

    def execute(self, *args):
        request = args[0]
        if type(request) == str and "CREATE TABLE" in args[0]:
            self.create_table(*args)
        else:
            client_request = args[0]
            func = client_request.func
            args = client_request.args
            kwargs = client_request.kwargs
            return func(*args, **kwargs)

    def apply_all(self, objects, filters=None, distinct=None, order_by=None, paginator=None, count_only=False):
        if filters:
            objects = filters.apply(objects)
        if distinct:
            objects = distinct.apply(objects)
        count = len(objects)
        if count_only:
            return count
        if order_by:
            objects = order_by.apply(objects)
        if paginator:
            objects = paginator.apply(objects)
        return objects, count

    def create_bulk(self, model, objects):
        pks = []
        pk_attname = model._meta.pk.attname
        for obj in objects:
            obj = self.create(model, obj)
            pks.append(getattr(obj, pk_attname))
        return pks

    def delete_bulk(self, model, filters):
        """

        :param params:
        :param kwargs:
        :return: ids The list of primary keys successfully deleted
        """
        ids = self.get_pks(model, filters)

        deleted_objects = []

        for id in ids:
            obj = self.delete(id, model)
            deleted_objects.append(obj)
        return deleted_objects

    def update_bulk(self, model, filters, update_with=()):
        """

        :param params:
        :param kwargs:
        :return: ids The list of primary keys successfully updated
        """
        ids = self.get_pks(model, filters)

        for id in ids:
            self.update(model, id, update_with=update_with)
        return ids

    def get_related(self, model):
        forward_fields = model._meta._forward_fields_map
        for fieldname, field in forward_fields.iteritems():
            if field.is_relation:
                column_name = field.attname
                fk_model = field.related_model
                fk_pk = fk_model._meta.pk.attname
                yield fieldname, column_name, fk_model, fk_pk

    def convert_to_tuple(self, object, fields):
        values = []
        for field in fields:
            value = object
            for attr in field:
                value = getvalue(value, attr)
            values.append(value)
        return tuple(values)

    def convert_to_tuples(self, objects, field_names):
        if objects:
            if type(objects[0]) == tuple:
                return objects
            elif type(objects[0]) == list:
                for index, obj in enumerate(objects):
                    objects[index] = tuple(obj)
                return objects
            else:
                list_of_tuples = []
                for object in objects:
                    list_of_tuples.append(self.convert_to_tuple(object, field_names))
                return list_of_tuples
        else:
            return []

    def close(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass