import threading

from django.shortcuts import render, get_object_or_404, reverse, HttpResponseRedirect
from django.utils import timezone
from .models import Member, TimelineBlock
from .forms import HoursForm, SignInTimeForm, BigTimeCorrectionForm, TimelineForm
from .constants import MEMBER_NAMES, SPREADSHEET_ID, SCOPE, START_DATE, END_DATE, G_SHEETS_ROW_SUM_COMMAND, GSPREAD_CREDS
from oauth2client.service_account import ServiceAccountCredentials
import datetime as dt
import gspread
import os


def index(request):
    member_list = Member.objects.all()
    form = request.POST
    if request.method == 'POST':
        selected_user = get_object_or_404(Member, name=request.POST.get('member_name'))
        return HttpResponseRedirect(reverse('member_profile', args=[selected_user.name]))
    return render(request, 'mainapp/index.html', {'member_list':member_list})


def view_member_profile(request, member_name):
    member = get_object_or_404(Member, name=member_name)
    if request.method == 'POST':
        form = TimelineForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data.get('text')
            if len(text) == 0:
                return member_signout(request, member_name)
            t = threading.Thread(target=timeline_block_bg_thread, args=[member, text])
            t.setDaemon(False)
            t.start()
            return member_signout(request, member_name)
    form = TimelineForm()
    timeline_list = list(reversed(TimelineBlock.objects.filter(member=member)))
    return render(request, 'mainapp/member_profile.html', {'member': member, 'form': form, 'timeline_list': timeline_list})


def timeline_block_bg_thread(member, text):
    newBlock = TimelineBlock()
    newBlock.content = text
    newBlock.member = member
    member.sign_out(timezone.now())
    newBlock.header = member.sign_in_time.strftime("%B %d, %Y")
    newBlock.subtitle = timeblock_subtitle_format(member.sign_in_time, member.sign_out_time)
    newBlock.save()


def member_signin(request, member_name):
    member = get_object_or_404(Member, name=member_name)
    member.sign_in(timezone.now())
    member.save()
    return HttpResponseRedirect(reverse('member_profile', args=[member.name]))


def member_signout(request, member_name):
    member = get_object_or_404(Member, name=member_name)
    member.sign_out(timezone.now())
    member.save()
    t = threading.Thread(target=member_signout_bg_thread, args=[member, member_name])
    t.setDaemon(False)
    t.start()
    return HttpResponseRedirect(reverse('member_profile', args=[member.name]))


def member_signout_bg_thread(member, member_name):
    update_spreadsheet(member_name, member.last_time_block / 60)
    verbose_log(member.get_name_display(), member.sign_in_time, member.sign_out_time)


def member_time_correction(request, member_name):
    member = get_object_or_404(Member, name=member_name)
    if request.method == 'POST':
        form = HoursForm(request.POST)
        if form.is_valid():
            t = threading.Thread(target=member_time_correction_bg_thread, args=[member, member_name, form])
            t.setDaemon(False)
            t.start()
            return HttpResponseRedirect(reverse('member_profile', args=[member.name]))
    else:
        form = HoursForm()
    return render(request, 'mainapp/member_time_correction.html', {'member':member, 'form':form})


def member_time_correction_in(request, member_name):
    member = get_object_or_404(Member, name=member_name)
    if request.method == 'POST':
        form = SignInTimeForm(request.POST)
        if form.is_valid():
            t = threading.Thread(target=member_time_correction_in_bg_thread, args=[member, form])
            t.setDaemon(False)
            t.start()
            return HttpResponseRedirect(reverse('member_profile', args=[member.name]))
    else:
        form = SignInTimeForm()
    return render(request, 'mainapp/member_time_correction_in.html', {'member': member, 'form': form})


def member_correction(request, member_name):
    member = get_object_or_404(Member, name=member_name)
    if request.method == 'POST':
        form = BigTimeCorrectionForm(request.POST)
        if form.is_valid():
            t = threading.Thread(target=member_correction_bg_thread, args=[member, form])
            t.setDaemon(False)
            t.start()
            return HttpResponseRedirect(reverse('member_profile', args=[member.name]))
    else:
        form =BigTimeCorrectionForm
    return render(request, 'mainapp/member_correction.html', {'member':member, 'form':form})


def whos_in(request):
    member_list = Member.objects.all()
    return render(request, 'mainapp/whos_in.html', {'member_list': member_list})


def group_timeline(request):
    timelinelist = list(reversed(TimelineBlock.objects.all()))
    return render(request, 'mainapp/group_timeline.html', {'timelinelist': timelinelist})


# -----------------NON-VIEW FUNCTIONS----------------------------------------------


def member_time_correction_bg_thread(member, member_name, form):
    hours_to_add = float(form.cleaned_data.get('hours'))
    print(hours_to_add)
    new_signed_out_dt = member.sign_in_time + dt.timedelta(hours=hours_to_add)
    print(new_signed_out_dt)
    member.sign_out_time = new_signed_out_dt
    member.total_time += int(hours_to_add * 60)
    member.is_signed_in = False
    member.save()
    update_spreadsheet(member_name, hours_to_add)
    verbose_log(member.get_name_display(), member.sign_in_time, member.sign_out_time, 'Manually Entered (Sign out)')


def member_time_correction_in_bg_thread(member, form):
    new_time_in = form.cleaned_data.get('time_signed_in')
    new_dt_in = dt.datetime.combine(dt.date.today(), new_time_in)
    member.sign_in_time = new_dt_in
    member.is_signed_in = True
    member.save()
    verbose_log(member.get_name_display(), member.sign_in_time, dt.datetime.now(), 'Manually Entered (Sign in)')


def member_correction_bg_thread(member, form):
    date = form.cleaned_data.get('date')
    hours = float(form.cleaned_data.get('hours'))
    date = dt.datetime.combine(date, dt.datetime.now().time())
    update_spreadsheet_by_day(member.name, hours, date)
    member.total_time += int(hours * 60)
    member.save()
    verbose_log(member.get_name_display(), timezone.now(), timezone.now(), 'Manually Entered (Backlog)')


# get_day_one_week_from(dt.datetime(2018,6,3)) returns 2018-06-10 00:00:00 (datetime object)
def get_day_one_week_from(date):
    return date+dt.timedelta(days=7)  # .strftime('%m/%d/%Y')


# get_week_list_dates_from(dt.datetime(2018,6,3)) returns ['06/03/2018', '06/04/2018', '06/05/2018', '06/06/2018', '06/07/2018', '06/08/2018', '06/09/2018']
def get_week_list_dates_from(date):
    ans = [date.strftime('%m/%d/%Y')]
    for i in range(1, 7):
        ans.append((date+dt.timedelta(days=i)).strftime('%m/%d/%Y'))
    return ans


# Passing MEMBER_NAMES returns ['Priya Aggarwal', 'Stephanie Budhan', ... , 'Sarah Vincent']
def verbose_list_from_choices(choices):
    ans = []
    for tup in choices:
        ans.append(tup[1])
    return ans


def short_list_from_choices(choices):
    ans = []
    for tup in  choices:
        ans.append(tup[0])
    return ans


# You know what this does
def is_sunday(date):
    return date.weekday() == 6  # Day 6 is Sunday in Python


def get_list_of_weeks(start_date, end_date):
    if not is_sunday(start_date) or not is_sunday(end_date):
        return ['One of the dates given is not a Sunday or is not a datetime.']
    ans = []
    while(True):
        ans.append(get_week_list_dates_from(start_date))
        start_date = get_day_one_week_from(start_date)
        if start_date == end_date:
            return ans


def timeblock_subtitle_format(time1, time2):
    return time1.strftime('%I:%M') + ' - ' + time2.strftime('%I:%M')


def generate_spreadsheet_template():
    list_of_weeks = get_list_of_weeks(START_DATE, END_DATE)
    spreadsheet_template = []
    for week in list_of_weeks:
        header = ['Week of '+week[0]]
        header += get_week_list_dates_from(dt.datetime.strptime(week[0], '%m/%d/%Y'))
        header.append('Total Hours (Week)')
        for member in verbose_list_from_choices(MEMBER_NAMES):
            header.append(member)
            header += [0]*7  # [0,0,0,0,0,0,0]
            header.append(G_SHEETS_ROW_SUM_COMMAND)
        spreadsheet_template += header
    dirname = os.path.dirname(__file__)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        os.path.join(dirname, GSPREAD_CREDS),
        SCOPE
    )
    gc = gspread.authorize(credentials)
    wks = gc.open_by_key(SPREADSHEET_ID)
    worksheet = wks.sheet1
    template_range = 'A1:I' + str(int(len(spreadsheet_template)/9))
    cell_list = worksheet.range(template_range)
    for cell, new_cell_value in zip(cell_list, spreadsheet_template):
        cell.value = new_cell_value

    worksheet.update_cells(cell_list, value_input_option='USER_ENTERED')


def update_spreadsheet_by_day(username, value, day):
    dirname = os.path.dirname(__file__)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        os.path.join(dirname, GSPREAD_CREDS),
        SCOPE
    )
    gc = gspread.authorize(credentials)
    wks = gc.open_by_key(SPREADSHEET_ID)
    worksheet = wks.sheet1
    current_date = '{d.month}/{d.day}'.format(d=day)
    current_date_cell = worksheet.findall(current_date)[0]
    row_index = short_list_from_choices(MEMBER_NAMES).index(username) + 1
    user_cell_row = current_date_cell.row + row_index
    user_cell_col = current_date_cell.col
    user_cell_value = float(worksheet.cell(user_cell_row, user_cell_col).value)
    worksheet.update_cell(user_cell_row, user_cell_col, user_cell_value+value)


def update_spreadsheet(username, value):
    dirname = os.path.dirname(__file__)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        os.path.join(dirname, GSPREAD_CREDS),
        SCOPE
    )
    gc = gspread.authorize(credentials)
    wks = gc.open_by_key(SPREADSHEET_ID)
    worksheet = wks.sheet1
    current_date = '{d.month}/{d.day}'.format(d=dt.datetime.now())
    current_date_cell = worksheet.findall(current_date)[0]
    row_index = short_list_from_choices(MEMBER_NAMES).index(username) + 1
    user_cell_row = current_date_cell.row + row_index
    user_cell_col = current_date_cell.col
    user_cell_value = float(worksheet.cell(user_cell_row, user_cell_col).value)
    worksheet.update_cell(user_cell_row, user_cell_col, user_cell_value+value)


def verbose_log(member_name, signed_in, signed_out, notes='Successful with no errors'):
    dirname = os.path.dirname(__file__)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        os.path.join(dirname, GSPREAD_CREDS),
        SCOPE
    )
    gc = gspread.authorize(credentials)
    wks = gc.open_by_key(SPREADSHEET_ID)
    worksheet = wks.worksheet("Verbose Log")
    worksheet.append_row([member_name, str(signed_in), str(signed_out), str(signed_out - signed_in), notes], value_input_option='USER_ENTERED')
