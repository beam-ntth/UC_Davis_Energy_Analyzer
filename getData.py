from ocs_sample_library_preview import OCSClient
import configparser
import io
import os
import json
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
from getPpl import get_num_people
from getPrice import get_num_price

from ocs_hackdavis import (
    ucdavis_buildings,  # list of campus buildings
    ucdavis_ceeds_of,  # list of CEED element of a building (Electricity, Steam, Chilled Water, etc)
    ucdavis_streams_of,  # The list of all OCS data streams for a building and CEED pair
    ucdavis_building_metadata,  # Metadata for a building: building code, lat/long, usage, etc.
    ocs_stream_interpolated_data,  # Interpolated data from a stream given a time range + interpolation interval
    ucdavis_outside_temperature,  # Outside temperature at UC Davis for a given a time range + interpolation interval
)

config_text = u"""
; IMPORTANT: replace these values with those provided by OSIsoft
[Configurations]
Namespace = UC__Davis

[Access]
Resource = https://dat-b.osisoft.com
Tenant = 65292b6c-ec16-414a-b583-ce7ae04046d4
ApiVersion = v1-preview

[Credentials] 
ClientId = 82fca0c2-3004-42c0-81cf-cc6968df1f47
ClientSecret = 3VYy318vxlFGKVuQ4+toahSyg7IqWUVKiGHJDvH/IvY=
"""

config = configparser.ConfigParser(allow_no_value=True)
config.read_file(io.StringIO(config_text))

ocs_client = OCSClient(
    config.get("Access", "ApiVersion"),
    config.get("Access", "Tenant"),
    config.get("Access", "Resource"),
    config.get("Credentials", "ClientId"),
    config.get("Credentials", "ClientSecret"),
)

namespace_id = config.get("Configurations", "Namespace")
# print(f"namespace_id: '{namespace_id}'")

all_buildings = ['ARC Pavilion', 'Academic Surge Building', 'Activities and Recreation Center',
                 'Advanced Materials Research Laboratory', 'Advanced Transportation Infrastructure Research Center',
                 'Aggie Stadium', 'Agronomy Field Laboratory', 'Animal Building', 'Animal Resource Service J1',
                 'Animal Resource Service M3', 'Animal Resource Service N1', 'Ann E. Pitzer Center',
                 'Antique Mechanics Trailer', 'Aquatic Biology & Environmental Science Bldg', 'Art Building',
                 'Art Building Annex', 'Art, Music, Wright Halls', 'Asmundson Annex', 'Asmundson Hall', 'Bainer Hall',
                 'Bowley Head House', 'Briggs Hall', 'California Hall', 'Campus Data Center',
                 'Cellular Biology Laboratory', 'Center for Companion Animal Health', 'Center for Comparative Medicine',
                 'Center for Health & Environment Clinical Medicine',
                 'Center for Health & Environment Office & Laboratory',
                 'Center for Health & Environment Toxic Pollutant Laboratory', 'Central Cage Wash Facility',
                 'Chemistry', 'Chemistry Annex', 'Cole A', 'Cole B', 'Conference Center', 'Contained Research Facility',
                 'Cruess Hall', 'Dairy Cattle Feed', 'Dairy Cattle Shed', 'Dairy Tower',
                 'Earth and Physical Sciences Building', 'Environmental Services Facility Headquarters',
                 'Equestrian Center Caretaker Trailer', 'Equestrian Center Covered Arena', 'Everson Hall',
                 'FPS Trinchero Building', 'Facilities Electrical Annex', 'Freeborn Hall', 'Gallagher Hall',
                 'Genome & Biomedical Sciences Facility', 'Geotechnical Modeling Facility', 'Ghausi Hall', 'Giedt Hall',
                 'Gourley Clinical Teaching Center', 'Growth Chamber Building T1', 'Growth Chamber Building T2',
                 'Haring Hall', 'Hart Hall', 'Heitman Staff Learning Center', 'Hickey Gym', 'Hickey Pool',
                 'Hoagland Hall', 'Hopkins Services Center Parking Lot', 'Hopkins Services Complex',
                 'Hopkins Services Complex Auxiliary Receiving', 'Housing Administration', 'Hunt Hall',
                 'Hutchison Child Development Center', 'Hutchison Hall', 'Hutchison Recreation Field Lights',
                 'IET Communications Resources', 'International Center', 'Jackson Sustainable Winery', 'Jungerman Hall',
                 'Kemper Hall', 'Kerr Hall', 'King Hall', 'Leukemia Barn', 'Leukemia Lab', 'Life Sciences', 'Maddy Lab',
                 'Mann Laboratory', 'Mathematical Sciences Building', 'Medical Sciences I B', 'Medical Sciences I D',
                 'Memorial Union', 'Meyer Hall', 'Mrak Hall', 'Music Building',
                 'Office of Research (1850 Research Park Drive)', 'Olson Hall', 'PES Tennis Courts',
                 'Parsons Seed Certification Center', 'Pavilion Parking Structure',
                 'Physical Sciences & Engineering Library', 'Physics Building', 'Plant & Environmental Sciences',
                 'Plant Reproductive Biology Facility', 'Primate Childhood Health & Disease Facility',
                 'Primate Controlled Environment Facility (CEF)', 'Primate Quarantine',
                 'Primate Respiratory Disease Center', 'Primate Shop Facility',
                 'Primate Virology & Immunology Laboratory', 'Pritchard VMTH', 'Quad Parking Structure',
                 'RMI Brewery, Winery, and Food Pilot Facility', 'Roessler Hall', 'Schaal Aquatic Center',
                 'School of Education Building', 'Sciences Lab Building', 'Segundo Dining Commons',
                 'Segundo High Rises', 'Segundo Regan', 'Segundo Services Center', 'Shields Library',
                 'Shrem Museum of Art', 'Silo Bike Barn', 'Social Sciences & Humanities', 'Sprocket Building',
                 'Sproul Hall', 'Storer Hall', 'Student Affairs Annex', 'Student Community Center',
                 'Student Health & Wellness Center', 'Swine Teaching and Research Facility', 'TAPS C&E',
                 'Temporary Building 144', 'Temporary Building 178', 'Temporary Building 184', 'Tercero 1', 'Tercero 3',
                 'Tercero 4', 'Tercero Dining Commons', 'The Barn', 'The Grove', 'Thurman Laboratory',
                 'Translational Shared Research Facility', 'Transportation and Parking Services', 'Tupper Hall',
                 'University Extension Building', 'VMTH Surgical', 'VMTH Ward', 'Valley Hall',
                 'Vet Med Equine Athletic Performance Lab', 'Vet Med Lab Animal A Beach Lab',
                 'Vet Med Large Animal Facility', 'Vet Med Student Services and Administration Center',
                 'Veterinary Medicine 2', 'Voorhies Hall', 'Walker Hall', 'Water Science & Engineering Hydraulic L2',
                 'Watershed Science Facility', 'Wellman Hall', 'Western Human Nutrition Research Center (WHNRC)',
                 'Wickson Hall', 'Wright Hall', 'Young Hall']

def convert_date_one_month(date):
    if int(date[5:7]) == 1:
        return str(int(date[:4])-1) + "-12" + date[7:]
    if int(date[5:7]) == 12 or int(date[5:7]) == 11:
        return date[:5] + str(int(date[5:7])-1) + date[7:]
    else:
        return date[:5] + '0' + str(int(date[5:7])-1) + date[7:]

def convert_date_one_day(date):
    year = int(date[:4])
    month = int(date[5:7])
    day = int(date[8:])
    current = datetime.datetime(year, month, day)
    one_day = datetime.timedelta(days=1)
    current = current-one_day

    return str(current)[:10]

class Building:
    def __init__(self, cost, construct, primary, building, value):
        self.cost = cost
        self.construct = construct
        self.primary = primary
        self.value = value
        self.diff = -1
        self.building = building
        self.lat = 0
        self.long = 0
        self.mgsf = 0
        self.rank = 0
        self.caan = 0
        self.avg_ppl = 0
        self.avg_price = -1


def get_consume_ranking(day, ceed, reverse=False):
    all_result = []
    for building in all_buildings:
        building_attri = ucdavis_building_metadata(ocs_client, namespace_id, building)
        cost = building_attri['Annual Cost']
        construct = building_attri['Construction Date']
        if building_attri['Primary Usage (Type)'] == 0.0:
            primary = 'Unspecified'
        else:
            primary = building_attri['Primary Usage (Type)']

        try:
            # Step 1: get the stream Id
            stream_id = ucdavis_streams_of(building, ceed)["MonthlyUsage"]

            # Step 2) request interpolated data
            # NOTE 1: difference between endIndex and startIndex should be 31 days or less
            # NOTE 2: interpolation interval cannot be less than 2 minutes
            result = ocs_stream_interpolated_data(
                ocs_client,
                namespace_id,
                stream_id,
                start=day,  # UTC -- 2017-03-01
                end=day,
                interval=1440,  # 1 day
            )

        except:
            continue

        if result and isinstance(result, list):
            # print(building, result)
            try:
                value = result[0]['Value']
                obj = Building(cost, construct, primary, building, value)
                all_result.append(obj)
            except:
                pass

    all_result.sort(key= lambda x: x.value, reverse=reverse)
    for i in range(len(all_result)):
        all_result[i].rank = i+1

    return all_result

def get_save_ranking(day, ceed, reverse=False):
    all_result = []
    for building in all_buildings:
        building_attri = ucdavis_building_metadata(ocs_client, namespace_id, building)
        cost = building_attri['Annual Cost']
        construct = building_attri['Construction Date']

        if building_attri['Primary Usage (Type)'] == 0.0:
            primary = 'Unspecified'
        else:
            primary = building_attri['Primary Usage (Type)']

        try:

            # Step 1: get the stream Id
            stream_id = ucdavis_streams_of(building, ceed)["MonthlyUsage"]
            # Step 2) request interpolated data
            # NOTE 1: difference between endIndex and startIndex should be 31 days or less
            # NOTE 2: interpolation interval cannot be less than 2 minutes
            # print(convert_date_one_day(day))

            result = ocs_stream_interpolated_data(
                ocs_client,
                namespace_id,
                stream_id,
                start=convert_date_one_day(day),  # UTC -- 2017-03-01
                end=day,
                interval=1440,  # 1 day
            )

        except:
            continue

        print(result)

        if result and isinstance(result, list):
            try:
                preval = result[0]['Value']
                value = result[1]['Value']
                print(preval, value)
                obj = Building(cost, construct, primary, building, value)
                obj.diff = round(value-preval, 2)
                all_result.append(obj)
            except:
                pass

    all_result.sort(key=lambda x: x.diff, reverse=reverse)
    for i in range(len(all_result)):
        all_result[i].rank = i + 1

    return all_result

def get_detail(name, date, ceed):
    building_attri = ucdavis_building_metadata(ocs_client, namespace_id, name)
    cost = building_attri['Annual Cost']
    construct = building_attri['Construction Date']
    lat = building_attri['Latitude']
    long = building_attri['Longitude']
    mgsf = building_attri['Maintained Gross Sq. Ft.']
    caan = str(int(building_attri['CAAN']))

    if building_attri['Primary Usage (Type)'] == 0.0:
        primary = 'Unspecified'
    else:
        primary = building_attri['Primary Usage (Type)']

    # Step 1: get the stream Id
    stream_id = ucdavis_streams_of(name, ceed)["MonthlyUsage"]

    # Step 2) request interpolated data
    # NOTE 1: difference between endIndex and startIndex should be 31 days or less
    # NOTE 2: interpolation interval cannot be less than 2 minutes

    print(date)
    print(convert_date_one_month(date))

    result = ocs_stream_interpolated_data(
        ocs_client,
        namespace_id,
        stream_id,
        start=convert_date_one_month(date),  # UTC
        end=date,
        interval=1440,  # 1 day
    )

    if os.path.exists('./static/images/' + caan + '.png'):
        os.unlink('./static/images/' + caan + '.png')
        plt.clf()

    plt.figure(figsize=(15, 11), dpi=150)
    plt.title(name + ' - 1 month')

    all_value = []
    all_date = []

    for r in result:
        all_date.append(r['Timestamp'][:10])
        all_value.append(r['Value'])

    plt.grid(True)
    plt.plot(all_value, label=ceed)
    plt.xlabel("Date (Year-Month-Day)")
    plt.ylabel("Amount of Energy Used (kBth)")
    plt.xticks(np.arange(len(all_date)), all_date ,rotation=45)
    plt.legend()
    plt.savefig('./static/images/' + caan + '.png')
    print(all_value)
    value = all_value[-1]

    building = Building(cost, construct, primary, name, value)
    building.lat = lat
    building.long = long
    building.mgsf = mgsf
    building.caan = caan

    avg_ppl = get_num_people(date, caan)
    if avg_ppl == 0:
        avg_ppl = "Not Tracked"

    building.avg_ppl = avg_ppl

    avg_price = get_num_price(date)
    building.avg_price = avg_price

    return building

if __name__ == '__main__':
    # print(get_detail("Tupper Hall", "2020-01-02", "Electricity"))
    # print(get_consume_ranking('2017-03-01', 'Electricity'))
    print(get_save_ranking('2020-01-01', 'Electricity'))
    # print(convert_date_one_day('2020-01-01'))