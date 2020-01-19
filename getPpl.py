import pandas as pd

# List of all the buildings
caanlist = ['4632', '4442', '4799', '3422', '4273', '4882', '3961', '3961B', '4220', '4784', '3320', '4708', '3972', '4869', '4633', '3839', '4658', '4786', '4725', '4835', '3207', '4728', '3421', '3788', '4871', '3814', '4302', '4051', '4274', '4683', '4716', '3841', '4821', '4556', '4854', '3842', '4428', '4429', '3460', '3970', '3803', '4726', '4266', '4243', '4787', '4444', '3237', '4265', '4898', '4802', '3390', '4792', '4803', '4977', '4656', '3815', '4897', '4073', '4098', '4828', '4023', '4567', '4427', '4466', '4793', '4820', '4822', '4795', '4267', '4050', '3351', '4833', '3266']

def get_num_people (date, caan):
    year = int(date[:4])
    month = int(date[5:7])
    day = int(date[8:])

    # Handling Edge Cases
    if caan == '0':
        return 0

    if caan not in caanlist:
        return 0

    # caandic = {}
    # date format is 3/15/2019
    date = str(month) + "/" + str(day) + "/" + str(year)
    data=pd.read_csv('./static/csv/ucdavis_wifi_data.csv')
    target_row = -1

    for i in range(0, data.index.stop,96):

        if data.loc[i]['Asset Number/CAAN'][:8] == date or data.loc[i]['Asset Number/CAAN'][:9] == date or data.loc[i]['Asset Number/CAAN'][:10] == date:
            target_row = i
            break

    sum = 0.0
    for row in range(target_row, target_row+96):
        if data.loc[row][caan] != 'No Data':
            sum += float(data.loc[row][caan])
        else:
            continue

    return round(sum/97.0)


    # for caan in caanlist:
    #     sum=0.0
    #     for j in range(target_row, target_row+96):
    #         if data.loc[j][caan] != 'No Data':
    #             sum += float(data.loc[j][caan])
    #         else:
    #             continue
    #     caandic[caan]= sum/97.0
    #
    # print(caandic)
