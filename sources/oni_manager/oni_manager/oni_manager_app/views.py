# Create your views here.

from django.http import HttpResponse
from django.contrib.auth import authenticate

from django.contrib.auth import login


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
    
    