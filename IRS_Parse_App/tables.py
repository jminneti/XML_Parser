import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from .models import Document

class UploadsTable(tables.Table):
  select = tables.CheckBoxColumn(accessor="pk")
  
  class Meta:
    model = Document
    template_name = 'django_tables2/bootstrap.html'
    sequence = ("select", "...")
