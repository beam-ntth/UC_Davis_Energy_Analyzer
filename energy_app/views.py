from django.shortcuts import render
from getData import get_consume_ranking, get_detail, get_save_ranking

class query:
    def __init__(self, cat, date, ceed):
        self.category = cat
        self.date = date
        self.ceed = ceed

# Create your views here.
def index(request):
    return render(request, 'energy_app/index.html')


def analyze(request):
    category = request.GET['category']
    date = request.GET['date']
    ceed = request.GET['ceed']
    data_dict = {}
    data_save_dict = {}

    if category == 'use-most':
        data_dict = get_consume_ranking(date, ceed=ceed, reverse=True)
    elif category == 'use-least':
        data_dict = get_consume_ranking(date, ceed=ceed)
    elif category == 'save-most':
        data_save_dict = get_save_ranking(date, ceed=ceed)
    else:
        data_save_dict = get_save_ranking(date, ceed=ceed, reverse=True)

    if category == 'use-most':
        category = 'Most Energy Consumption'
    elif category == 'use-least':
        category = 'Least Energy Consumption'
    elif category == 'save-most':
        category = 'Save Most Energy'
    else:
        category = 'Save Least Energy'

    print(data_save_dict)
    all_dict = {'data': data_dict, 'data_save': data_save_dict, 'query': query(category, date, ceed)}
    return render(request, 'energy_app/index.html', context=all_dict)

def detail(request):
    name = request.GET['name']
    date = request.GET['date']
    ceed = request.GET['ceed']
    bld_detail = get_detail(name, date, ceed)
    electric_unit = float(bld_detail.value)/3412
    bld_detail.avg_price = round(float(bld_detail.avg_price)*electric_unit, 2)
    bld_detail.avg_price = '{:,.2f}'.format(bld_detail.avg_price)
    all_dict = {'detail': bld_detail, 'util': query(name, date, ceed)}

    return render(request, 'energy_app/index.html', context=all_dict)
