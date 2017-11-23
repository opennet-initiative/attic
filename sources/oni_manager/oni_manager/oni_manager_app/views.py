# Create your views here.

from django.contrib.auth.decorators import login_required

from django.template import Context, loader
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.template import RequestContext
from django.core.mail import send_mail

from forms import SignupForm
from models import Mitglied
from oni_manager.oni_manager_app.forms import ownDataForm
        

@login_required
def viewMember(request, member_id):    
    member = Mitglied.objects.get(pk=member_id)  
    form = ownDataForm()
    t = loader.get_template('members/one_member.html')
    c = Context({
        'user': request.user,
        'fullname': member.user.get_full_name(),
        'member': member,
        'form': form,
    })
    return HttpResponse(t.render(c))


def home_view(request):
    if request.user.is_authenticated():
        mitglied=Mitglied.objects.get(user=request.user.id)
        return viewMember(request,mitglied.id)
    else:
        return redirect('/login/')

def logout_view(request):
    logout(request)
    return redirect('/')

def signup_thanks_view(request):
    t = loader.get_template('registration/signup.html')
    c = RequestContext(request, {
    })
    return HttpResponse(t.render(c))

def signup(request):
    if request.user.is_authenticated():
        return redirect('/')
    form = SignupForm()
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            send_mail(username, 'Here is the message.', 'gimbar@gmail.com',['gimbar@gmail.com'], fail_silently=False)
            return HttpResponse("Mail for signup sent")
 
    t = loader.get_template('registration/signup.html')
    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))
