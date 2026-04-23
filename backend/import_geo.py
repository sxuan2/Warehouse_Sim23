import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from warehouses.models import Country, Region, CountryTimezone

def import_data():
    data = {
        'US': {
            'name': 'United States',
            'regions': [('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('DC', 'District of Columbia'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')],
            'timezones': [('America/New_York', 'Eastern Time'), ('America/Chicago', 'Central Time'), ('America/Denver', 'Mountain Time'), ('America/Los_Angeles', 'Pacific Time'), ('America/Anchorage', 'Alaska Time'), ('Pacific/Honolulu', 'Hawaii Time')]
        },
        'CA': {
            'name': 'Canada',
            'regions': [('AB', 'Alberta'), ('BC', 'British Columbia'), ('MB', 'Manitoba'), ('NB', 'New Brunswick'), ('NL', 'Newfoundland'), ('NS', 'Nova Scotia'), ('NT', 'Northwest Territories'), ('NU', 'Nunavut'), ('ON', 'Ontario'), ('PE', 'Prince Edward Island'), ('QC', 'Quebec'), ('SK', 'Saskatchewan'), ('YT', 'Yukon')],
            'timezones': [('America/St_Johns', 'Newfoundland'), ('America/Halifax', 'Atlantic'), ('America/Toronto', 'Eastern'), ('America/Winnipeg', 'Central'), ('America/Edmonton', 'Mountain'), ('America/Vancouver', 'Pacific')]
        }
    }

    for code, info in data.items():
        c, _ = Country.objects.get_or_create(code=code, defaults={'name': info['name']})
        for r_code, r_name in info['regions']:
            Region.objects.get_or_create(country=c, code=r_code, defaults={'name': r_name})
        for t_id, t_name in info['timezones']:
            CountryTimezone.objects.get_or_create(country=c, timezone_id=t_id, defaults={'display_name': t_name})
    print("Done.")

if __name__ == '__main__': import_data()