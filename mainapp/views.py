from django.shortcuts import render, get_object_or_404, reverse, HttpResponseRedirect
from django.utils import timezone
from .models import Member
# Create your views here.


def index(request):
    member_list = Member.objects.all()
    form = request.POST
    if request.method == 'POST':
        selected_user = get_object_or_404(Member, name=request.POST.get('member_name'))
        return HttpResponseRedirect(reverse('member_profile', args=[selected_user.name]))
    return render(request, 'mainapp/index.html', {'member_list':member_list})


def view_member_profile(request, member_name):
    member = get_object_or_404(Member, name=member_name)
    return render(request, 'mainapp/member_profile.html', {'member':member})


def member_signin(request, member_name):
    member = get_object_or_404(Member, name=member_name)
    member.sign_in(timezone.now())
    member.save()
    return HttpResponseRedirect(reverse('member_profile', args=[member.name]))


def member_signout(request, member_name):
    member = get_object_or_404(Member, name=member_name)
    member.sign_out(timezone.now())
    member.save()
    return HttpResponseRedirect(reverse('member_profile', args=[member.name]))