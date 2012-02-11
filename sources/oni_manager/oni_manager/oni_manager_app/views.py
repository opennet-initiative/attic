# Create your views here.

from django.contrib.auth.decorators import login_required

from django.template import Context, loader
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import logout

from forms import SignupForm
from models import Mitglied
        

@login_required
def viewMember(request, member_id):
    if request.user.is_authenticated():
        return redirect('/')
    
    member = Mitglied.objects.get(pk=member_id)
    #form = MemberForm(instance=member)    
    t = loader.get_template('members/one_member.html')
    c = Context({
        'user': request.user,
        'fullname': member.user.get_full_name(),
        'member': member,
        #'form': form,
    })
    return HttpResponse(t.render(c))

def home_view(request):
    if request.user.is_authenticated():
        return HttpResponse("logged int")
    return HttpResponse("not logged in")

def logout_view(request):
    logout(request)
    return redirect('/')

def signup(request):
    if request.user.is_authenticated():
        return redirect('/')
    
    form = SignupForm()
    t = loader.get_template('registration/signup.html')
    c = Context({
        'form': form,
    })
    return HttpResponse(t.render(c))
   
def register(request):
    if request.user.is_authenticated():
        return redirect('/')
    
    
    print request.POST