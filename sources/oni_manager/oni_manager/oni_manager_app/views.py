# Create your views here.

from django.contrib.auth.decorators import login_required

from django.template import Context, loader
from django.http import HttpResponse

from forms import SignupForm
from models import Mitglied
        

@login_required
def viewMember(request, member_id):
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


def signup(request):
    form = SignupForm()
    t = loader.get_template('registration/signup.html')
    c = Context({
        'form': form,
    })
    return HttpResponse(t.render(c))
   
    
    