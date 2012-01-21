'''
Created on 21.01.2012

@author: Jonas
'''

from models import Bankkonto
from models import Anschrift
from models import Mitglied
from django.contrib import admin

admin.site.register(Bankkonto)
admin.site.register(Anschrift)
admin.site.register(Mitglied)