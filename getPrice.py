import pandas as pd

def get_num_price(date):
    year = int(date[:4])
    month = int(date[5:7])
    day = int(date[8:])

    # date format is 3/15/2019
    date = str(month) + "/" + str(day) + "/" + str(year)
    row=-1
    data=pd.read_csv('./static/csv/RealTimeMarketRate.csv')
    for i in range(0,data.index.stop,288):
        if data.loc[i]['Date'][:8] == date or data.loc[i]['Date'][:9] == date or data.loc[i]['Date'][:10] == date :
            row=i
            break

    sum=0.0
    for j in range(row,row+288):
        if data.loc[j]['Price'] != 'No Data':
                sum += float(data.loc[j]['Price'])
        else:
            continue

    return sum/289.0
    # print(str(sum/289.0))