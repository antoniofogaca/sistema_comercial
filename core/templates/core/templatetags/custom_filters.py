from django import template

register = template.Library()

@register.filter
def get_field_name(form_fields, field_name):
    """Retorna o verbose_name de um campo do formulário."""
    return form_fields[field_name].label if field_name in form_fields else field_name