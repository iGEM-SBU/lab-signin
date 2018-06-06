from django.contrib import admin
from django.urls import path
from django.shortcuts import HttpResponseRedirect
from .constants import MEMBER_NAMES
from .models import Member

from .models import Member

class MemberAdmin(admin.ModelAdmin):
    change_list_template = 'mainapp/admin_member_changelist.html'
    list_display = ('name', 'is_signed_in', 'total_time')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('populate/', self.populate_database),
        ]
        return my_urls + urls

    def populate_database(self, request):
        for member_name in MEMBER_NAMES:
            member = Member()
            member.name = member_name[0]
            member.save()
        return HttpResponseRedirect('../')

admin.site.register(Member, MemberAdmin)
