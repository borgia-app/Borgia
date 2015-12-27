from django.contrib import admin
from finances.models import *


admin.site.register(Transaction)
admin.site.register(Cheque)
admin.site.register(Cash)
admin.site.register(Lydia)

