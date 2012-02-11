'''
Created on 22.01.2012

@author: Jonas
'''

from django import forms
from django.forms import ModelForm
from oni_manager.oni_manager_app.models import Mitglied

class MemberForm(forms.ModelForm):
    class Meta():
        model = Mitglied
        
class LoginForm(forms.Form):
    username = forms.CharField( label="Benutzername" )
    password = forms.CharField( widget=forms.PasswordInput, label="Passwort" )
        
class SignupForm(forms.Form):
    username = forms.CharField( label="Benutzername" )
    firstname = forms.CharField( label="Vorname" )
    lastname = forms.CharField( label="Nachname" )
    email = forms.EmailField( label="Email" )
    password = forms.CharField( widget=forms.PasswordInput, label="Passwort" )
    telefon = forms.CharField( label="Telefon", max_length=100)
    geburtsdatum = forms.DateField( label="Geburtstdatum" )
    bankkonto = forms.CharField( label="Bankkonto" )
    anschrift = forms.CharField( label="Anschrift" )
    nickname = forms.CharField( label="Nicknames" )
    #foto = forms.ImageField( label="Foto", upload_to='avatars')
    
class ownDataForm(ModelForm):
    class Meta:
         model = Mitglied