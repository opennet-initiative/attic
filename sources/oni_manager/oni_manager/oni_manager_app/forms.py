'''
Created on 22.01.2012

@author: Jonas
'''

from django import forms 
from oni_manager.oni_manager_app.models import Mitglied

class MemberForm(forms.ModelForm):
    
    class Meta():
        model = Mitglied
        
class SignupForm(forms.Form):
    username = forms.CharField()
    firstname = forms.CharField()
    lastname = forms.TextInput()
    email = forms.EmailField()
    password = forms.PasswordInput()