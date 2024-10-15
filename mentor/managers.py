from django.db import models

class DynamicFieldsManager(models.Manager):
    def create(self, **kwargs):
        additional_info = kwargs.pop('additional_info', {})
        instance = super().create(**kwargs)
        instance.additional_info = additional_info
        instance.save()
        return instance

    def get_dynamic_fields(self, instance):
        """Return all dynamic fields as a dictionary."""
        if not hasattr(instance, 'additional_info'):
            raise AttributeError(f"{instance} does not have 'additional_info'.")
        return instance.additional_info

    def set_dynamic_field(self, instance, key, value):
        """Set or update a dynamic field."""
        if not hasattr(instance, 'additional_info'):
            raise AttributeError(f"{instance} does not have 'additional_info'.")
        
        instance.additional_info[key] = value
        instance.save()

    def get_dynamic_field(self, instance, key):
        """Get a dynamic field by key."""
        if not hasattr(instance, 'additional_info'):
            raise AttributeError(f"{instance} does not have 'additional_info'.")
        
        return instance.additional_info.get(key, None)

    def update_dynamic_fields(self, instance, fields_dict):
        """Update multiple dynamic fields at once."""
        if not hasattr(instance, 'additional_info'):
            raise AttributeError(f"{instance} does not have 'additional_info'.")

        for key, value in fields_dict.items():
            instance.additional_info[key] = value
        
        instance.save()
