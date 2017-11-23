'''
Created on 11.02.2012

@author: Jonas
'''

from datetime import datetime
import hashlib
from oni_manager.oni_manager_app.models import RegistrationSession
from oni_manager.oni_manager_app.models import Mitglied 
from django.contrib.auth.models import User

REGISTRATION_SENDER_EMAIL = 'noreply@opennet.de'
REGISTRATION_SESSION_ATTR = 'has_registered'

class RegistrationProcess(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        pass
    
    def __createUser(self, signupForm):
        username = signupForm.cleaned_data.get('username')
        firstname = signupForm.cleaned_data.get('firstname')
        lastname = signupForm.cleaned_data.get('lastname')
        email = signupForm.cleaned_data.get('email')
        password = signupForm.cleaned_data.get('password')
        telefon = signupForm.cleaned_data.get('telefon')
        geburtsdatum = signupForm.cleaned_data.get('geburtsdatum')
        bankkonto = signupForm.cleaned_data.get('bankkonto')
        anschrift = signupForm.cleaned_data.get('anschrift')
        nickname = signupForm.cleaned_data.get('nickname')
        status='nicht freigeschaltet'
        foerdermitglied=False
        
        user = User ( username=username, first_name=firstname, last_name=lastname, email=email, password=password)
        user.save()
        
        m = Mitglied(telefon=telefon, geburtsdatum=geburtsdatum, status=status, 
                   bankkonto=bankkonto, anschrift=anschrift, nickname=nickname, foerdermitglied=foerdermitglied)
        m.save()
        
        pass
    
    def __createRegistration(self, request):
        # check if this user has already 
        if request.session.get(REGISTRATION_SESSION_ATTR, True):
            return False
        
        # create registration key
        m = hashlib.sha1();
        m.update(request.session.session_key)
        m.update(request.POST)
        request.POST(str(datetime.now()))
        regKey = m.digest()
        
        # create Registration session with previously generated key
        reg = RegistrationSession( key=regKey,user=request.user )
        reg.save()
        
        # mark this session as registered
        request.session[REGISTRATION_SESSION_ATTR] = True
        return True 
        
    
    def register(self, request, signupForm):        
        if not self.__createRegistration(request):
            return False
        self.__createUser(signupForm)
        return True
    
    
    def activate(self, request):        
        pass
        