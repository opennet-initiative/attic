'''
Created on 21.01.2012

@author: Jonas
'''

from models import Bankkonto
from models import Anschrift
from models import Mitglied
from django.contrib import admin

#class AnschriftInline(admin.StackedInline):
#    model = Anschrift


class MitgliedAdmin(admin.ModelAdmin):
#    inlines = [AnschriftInline,]
    list_display = ('nickname', 'status','mitgliedseit',"foto")
    list_filter = ("status", 'mitgliedseit')
    ordering = ('status',)
    search_fields = ('nickname',)
    exclude=("user",)
    
    

admin.site.register(Bankkonto)
admin.site.register(Anschrift)
admin.site.register(Mitglied, MitgliedAdmin)