import datetime as dt
# Member Names (('username', 'verbose name'), ('username2', 'verbose name2'))
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

# Lab Info
START_DATE = dt.datetime(2018, 5, 27)
END_DATE = dt.datetime(2018, 8, 12)

# Google Sheets API/gspread Info
SPREADSHEET_ID = '1WdJKTDyZWeEFwS2MT7nIvaqaRlMd9Sgut71cvNMYp_M'
SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
GSPREAD_CREDS = 'gspread_creds.json'
G_SHEETS_ROW_SUM_COMMAND = '''=SUM(INDIRECT(CONCATENATE("B",ROW(),":H",ROW())))'''
