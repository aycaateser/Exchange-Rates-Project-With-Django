import datetime
from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from home.models import Currency
import xmldict
import requests
from datetime import date
import json


# Create your views here.
def index(request):
    today = date.today().strftime("%Y-%m-%d")
    url = "https://www.tcmb.gov.tr/kurlar/today.xml"
    if not Currency.objects.filter().first():  # yani db boş ise-ilk eleman yoksa
        response = requests.get(url)
        response = response.text
        result = xmldict.xml_to_dict(response)
        for currency in result["Tarih_Date"]["Currency"]:
            currency_buying = currency["ForexBuying"] if currency["ForexBuying"] else 0.0
            currency_selling = currency["ForexSelling"] if currency["ForexSelling"] else 0.0
            currency_data = Currency(currency_name=currency["CurrencyName"], currency_buying=currency_buying,
                                     currency_selling=currency_selling, currency_rate_date=today)
            currency_data.save()
    else:
        if today != Currency.objects.filter().last().currency_rate_date.strftime("%Y-%m-%d"):  # db dolu ve guncelle
            response = requests.get(url)
            response = response.text
            result = xmldict.xml_to_dict(response)
            for currency in result["Tarih_Date"]["Currency"]:
                currency_buying = currency["ForexBuying"] if currency["ForexBuying"] else 0.0
                currency_selling = currency["ForexSelling"] if currency["ForexSelling"] else 0.0
                currency_data = Currency(currency_name=currency["CurrencyName"], currency_buying=currency_buying,
                                         currency_selling=currency_selling, currency_rate_date=today)
                currency_data.save()
    currency_list = Currency.objects.filter(currency_rate_date=datetime.date.today()).values('currency_name',
                                                                                             'currency_buying',
                                                                                             'currency_selling',
                                                                                             'currency_rate_date')
    # [{'curreny_name': 'US DOLLAR, 'curreny_buying': decimal(), 'curreny_selling': decimal()}, {}]
    curreny_name_list = Currency.objects.values_list('currency_name').distinct()
    currency_diff_rate_list = curreny_diff_rate_calculation(curreny_name_list)
    #fark matchlemek
    for currency in currency_list:
        index_of_currency = list(currency_list).index(currency)
        # {'curreny_name': 'US DOLLAR, 'curreny_buying': decimal(), 'curreny_selling': decimal()}
        currency['currency_diff_rate'] = currency_diff_rate_list[index_of_currency]  # yeni dict fieldı
    # CURRENY_LİST İÇERİSİNDE OLAN VERİLİRİN ÖNCEKİ GÜNLE KARŞILAŞTIRARAK BİR YENİ FİELD EKLEMEK HEPSİNE
    currency_dict = {
        'currencies': currency_list
    }

    a = Currency.objects.values_list('currency_buying').filter(currency_name="EURO")
    print(type(a))
    b = list(a)
    print(type(b))
    print(b)

    return render(request, 'home/index.html', currency_dict)


def search_bar(request):
    if request.method == "GET":
        query = request.GET.get("q", None)
        if query:
            currency_query = Currency.objects.filter(currency_name__contains=query).values('currency_name',
                                                                                           'currency_buying',
                                                                                           'currency_selling',
                                                                                           'currency_rate_date').filter(
                currency_rate_date=datetime.date.today()) #sadece bugunun verilerini getir


        else:
            print("No information to show")
            currency_query = Currency.objects.values('currency_name', 'currency_buying', 'currency_selling',
                                                     'currency_rate_date')
            print("buradayım")
            print(type(currency_query))


  # [{'curreny_name': 'US DOLLAR, 'curreny_buying': decimal(), 'curreny_selling': decimal()}, {}]
    currency_list = Currency.objects.filter(currency_rate_date=datetime.date.today()).values('currency_name',
                                                                                             'currency_buying',
                                                                                             'currency_selling',
                                                                                             'currency_rate_date')
    # [{'curreny_name': 'US DOLLAR, 'curreny_buying': decimal(), 'curreny_selling': decimal()}, {}]
    curreny_name_list = Currency.objects.values_list('currency_name').distinct()
    currency_diff_rate_list = curreny_diff_rate_calculation(curreny_name_list)
    # fark matchlemek
    for currency in currency_query:
        index_of_currency_query = list(currency_list).index(currency)
        # {'curreny_name': 'US DOLLAR, 'curreny_buying': decimal(), 'curreny_selling': decimal()}
        currency['currency_diff_rate'] = currency_diff_rate_list[index_of_currency_query]  # yeni dict fieldı
    # CURRENY_LİST İÇERİSİNDE OLAN VERİLERİ ÖNCEKİ GÜNLE KARŞILAŞTIRARAK HEPSİNE YENİ BİR FİELD EKLER
    currency_dict = {
        'currencies': currency_list
    }

    return render(request, "home/index.html",{'currencies': currency_query})

@csrf_exempt
def conversion(request):
    if request.method == "POST":
        amount = request.POST.get('currencyAmount')
        currency_name = request.POST.get('currencyName')
        currency_list = calculation(int(amount), currency_name)
    else:
        currency_list = []
    currency_select = Currency.objects.values('currency_name').filter(currency_rate_date=datetime.date.today())
    # print(currency_select)
    return render(request, "home/calculate.html",
                  context={"currency_select": currency_select, "currency_list": currency_list})


def calculation(amount, currency_name):
    currency_list = Currency.objects.values('currency_name', 'currency_buying',
                                            'currency_selling').filter(currency_rate_date=datetime.date.today())
    convertion_currency_datas = Currency.objects.values('currency_buying', 'currency_selling').filter(
        currency_rate_date=datetime.date.today()).filter(currency_name=currency_name)
    for currency in currency_list:
        if currency['currency_selling'] == 0:
            currency['currency_selling'] = 1.0
        if currency['currency_buying'] == 0:
            currency['currency_buying'] = 1.0
        total_currency = float(convertion_currency_datas[0]['currency_buying']) * amount
        currency['currency_buying'] = round(total_currency / float(currency['currency_buying']), 2)
        total_currency = float(convertion_currency_datas[0]['currency_selling']) * amount
        currency['currency_selling'] = round(total_currency / float(currency['currency_selling']), 2)
        currency['converted_currency_amount'] = amount
        currency['converted_currency_name'] = currency_name
    return currency_list


def graph(request):
    euro_filter = Currency.objects.values_list('currency_rate_date', 'currency_buying',
                                               'currency_selling').filter(currency_name="EURO")
    print(euro_filter)
    graph_list = []
    for data in euro_filter:
        data = list(data)
        data[0] = int(data[0].strftime("%d"))
        data[1] = float(data[1])
        data[2] = float(data[2])
        graph_list.append(data)
    print(graph_list)
    return render(request, "home/graph.html", context={'graph_list': graph_list})


def curreny_diff_rate_calculation(curreny_name_list):
    curreny_diff_rate_list = []
    for currency in curreny_name_list:
        currency_buying_list = Currency.objects.filter(currency_name=currency[0]).values_list('currency_buying')
        if len(currency_buying_list) > 1:
            currency_buying_list = currency_buying_list[:2]
            result = float(currency_buying_list[1][0]) - float(currency_buying_list[0][0])
            result = (result / float(currency_buying_list[1][0])) * 100
            curreny_diff_rate_list.append(str(round(result, 2)) + '%')
        else:
            curreny_diff_rate_list.append("-")

    print(curreny_diff_rate_list)

    return curreny_diff_rate_list
