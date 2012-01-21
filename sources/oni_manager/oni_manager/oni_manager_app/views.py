# Create your views here.

from django.http import HttpResponse
from django.contrib.auth import authenticate

from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
 
def login(request):
    """Logs a user into the application."""
 
    if request.user.is_authenticated():
        return HttpResponse("a")
 
    # Initialize the form either fresh or with the appropriate POST data as the instance
    auth_form = AuthenticationForm(None, request.POST or None)
 
    # The form itself handles authentication and checking to make sure passowrd and such are supplied.
    if auth_form.is_valid():
        login(request, auth_form.get_user())
        return HttpResponse("b")
 
    return render(request, 'login.xhtml', {
        'auth_form': auth_form,
        'title': 'User Login'
    })

def loginOLD(request):
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(username=email, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            # Redirect to a success page.
        else:
            return HttpResponse("Your account had been disabled!")
    else:
        return HttpResponse("Not logged in!")
    
    