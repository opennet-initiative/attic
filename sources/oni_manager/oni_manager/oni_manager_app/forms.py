'''
Created on 22.01.2012

@author: Jonas
'''

from django.forms import ModelForm
from oni_manager.oni_manager_app.models import Mitglied

class MemberForm(ModelForm):
    
    class Meta():
        model = Mitglied