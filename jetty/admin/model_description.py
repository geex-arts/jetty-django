from django.contrib.contenttypes.models import ContentType

from jetty.filters.model import model_filter_class_factory
from jetty.serializers.model import model_serializer_factory
from jetty.serializers.model_detail import model_detail_serializer_factory
from jetty.views.model import model_viewset_factory


class JettyAdminModelDescription(object):
    def __init__(self, Model, fields=None, actions=list(), ordering_field=None):
        self.model = Model
        self.fields = fields

        for action in actions:
            action.init_meta()

        self.actions = actions
        self.ordering_field = ordering_field \
            if ordering_field in map(lambda x: x.name, self.get_model_fields()) \
            else None
        self.content_type = ContentType.objects.get_for_model(Model)
        self.field_names = list(map(lambda x: x.name, self.get_fields()))
        self.serializer = model_serializer_factory(Model, self.field_names + ['id'])
        self.detail_serializer = model_detail_serializer_factory(Model, self.field_names + ['id'])
        self.filter_class = model_filter_class_factory(Model, self.get_fields())
        self.queryset = Model.objects.all()
        self.viewset = model_viewset_factory(
            Model,
            self.filter_class,
            self.serializer,
            self.detail_serializer,
            self.queryset,
            self.actions,
            self.ordering_field
        )

    @property
    def viewset_url(self):
        return 'models/{}/{}'.format(self.content_type.app_label, self.content_type.model)

    def get_model_fields(self):
        return self.model._meta.get_fields()

    def get_fields(self):
        fields = self.get_model_fields()
        if self.fields:
            fields = filter(lambda x: x.name in self.fields or x.name == self.ordering_field, fields)
        return fields

    def serialize(self):
        return {
            'model': self.content_type.model,
            'app_label': self.content_type.app_label,
            'verbose_name': self.model._meta.verbose_name,
            'verbose_name_plural': self.model._meta.verbose_name_plural,
            'fields': map(lambda field: {
                'name': field.name,
                'verbose_name': field.verbose_name,
                'is_relation': field.is_relation,
                'related_model': self.serialize_model(field.related_model),
                'field': field.__class__.__name__,
                'editable': field.editable,
                'filterable': field.name in self.filter_class.Meta.fields
            }, self.get_fields()),
            'actions': map(lambda action: {
                'name': action._meta.name,
                'verbose_name': action._meta.verbose_name,
                'fields': map(lambda field: {
                    'name': field[0],
                    'verbose_name': field[1].label or field[0],
                    'related_model': self.serialize_model(field[1].queryset.model) if hasattr(field[1], 'queryset') else None,
                    'field': field[1].__class__.__name__
                }, action.get_fields().items()),
            }, map(lambda action: action(), self.actions)),
            'ordering_field': self.ordering_field
        }

    def serialize_model(self, Model):
        if not Model:
            return
        content_type = ContentType.objects.get_for_model(Model)
        return {
            'model': content_type.model,
            'app_label': content_type.app_label
        }
