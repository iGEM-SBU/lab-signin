from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
import datetime as dt
import gspread

MEMBER_NAMES = (
    ('paggarwal', 'Priya Aggarwal'),
    ('sbudhan', 'Stephanie Budhan'),
    ('wchiang', 'Woody Chiang'),
    ('dkwasniak', 'Dominika Kwasniak'),
    ('kledalla', 'Karthik Ledalla'),
    ('mlee', 'Matthew Lee'),
    ('nlo', 'Natalie Lo'),
    ('mmullin', 'Matthew Mullin'),
    ('lypan', 'Lin Yu Pan'),
    ('jrakhimov', 'Jennifer Rakhimov'),
    ('rruzic', 'Robert Ruzic'),
    ('mshah', 'Manvi Shah'),
    ('lvelikov', 'Lukas Velikov'),
    ('svincent', 'Sara Vincent')
)

START_DATE = dt.datetime(2018, 6, 3)
END_DATE = dt.datetime(2018, 8, 12)
G_SHEETS_ROW_SUM_COMMAND = '''=SUM(INDIRECT(CONCATENATE("B",ROW(),":H",ROW())))'''

# get_day_one_week_from(dt.datetime(2018,6,3)) returns 2018-06-10 00:00:00 (datetime object)
def get_day_one_week_from(date):
    return (date+dt.timedelta(days=7))  # .strftime('%m/%d/%Y')


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
        if(start_date == end_date):
            return ans


def api_test():
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

    SPREADSHEET_ID = '1WdJKTDyZWeEFwS2MT7nIvaqaRlMd9Sgut71cvNMYp_M'
    SCOPE = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('gspread_creds.json', SCOPE)
    gc = gspread.authorize(credentials)
    wks = gc.open_by_key(SPREADSHEET_ID)
    worksheet = wks.sheet1
    template_range = 'A1:I' + str(int(len(spreadsheet_template)/9))
    cell_list = worksheet.range(template_range)
    for cell, new_cell_value in zip(cell_list, spreadsheet_template):
        cell.value = new_cell_value

    worksheet.update_cells(cell_list, value_input_option='USER_ENTERED')




api_test()
# print(get_week_list_dates_from(dt.datetime(2018,6,3)))
# print(verbose_list_from_choices(MEMBER_NAMES))
#print(get_day_one_week_from(dt.datetime(2018,6,3)))
# print(get_list_of_weeks(dt.datetime(2018,6,3), dt.datetime(2018,8,12)))
