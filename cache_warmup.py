from services.incidence_service import IncidenceService
from services.municipality_service import MunicipalityService
from data_access.canton_data_access import CantonDataAccess
from configManager import ConfigManager
from datetime import timedelta
from app import requests_cache

# Clear the cache before warmup
# Otherwise we wouldn't really warmup up the cache because expire time of
# already cached requests will not be reset...
if requests_cache.is_installed():
    requests_cache.clear()

# Get all configured cantons from config
cantonsservice_urls = ConfigManager.get_instance().get_cantonservice_urls()
# Get date format from config
df = ConfigManager.get_instance().get_required_date_format()

# Set the date_from and date_to dates for warmup
date_from = date_to = CantonDataAccess.get_default_date().strftime(df)

print(f'Fetching for date_from {date_from} to date_to {date_to}')

# Loop through all the cantons
for canton, canton_data in cantonsservice_urls.items():

    # Only process canton if a server is configured
    if canton_data['url'] != '':
        print(f"Current canton {canton} with URL {canton_data['url']}")

        # Fetch all the municipalities for current canton
        municipalities, status = MunicipalityService.get_municipalities(canton)

        # Only continue if municipalities were fetched
        if municipalities is not None:
            for municipality in municipalities:
                print(f"Fetch incidence for canton: {municipality['canton']}, municipality: {municipality['bfsNr']}")
                incidence_data, status = IncidenceService.get_incidences(
                    municipality['canton'], date_from, date_to, municipality['bfsNr'])

                retry_count = 0

                # If there was no data for 'today' go back one or two days and try to load those
                # If incidence_data was None, the canton is not available (or threw an error), do not retry
                while retry_count < 3 and incidence_data == []:
                    retry_count += 1

                    delta_days = timedelta(days=retry_count)

                    # Call the incidence URL - THIS is what we want to cache
                    incidence_data, status = IncidenceService.get_incidences(municipality['canton'], (CantonDataAccess.get_default_date() - delta_days).strftime(
                        df), (CantonDataAccess.get_default_date() - delta_days).strftime(df), municipality['bfsNr'])
