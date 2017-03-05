# from django.shortcuts import render
# from django.db.models.aggregates import Sum
# from django.http import HttpResponseRedirect
# from django.template.context_processors import csrf
# from django.template.loader import  get_template
# from django.template import Context
# from django.shortcuts import render_to_response
# import json
# from django.shortcuts import HttpResponse
# from django.http import JsonResponse
# from models import *
# import pandas as pd
# import datetime as dt
#
# # Create your views here.
# def select(request):
#     select = int(request.GET["select"])
#     time = int(request.GET["time"])
#     times = ["cast(strftime('%H', receipt_date) AS TEXT)|| ':'|| cast(strftime('%M', receipt_date)/10*10 AS TEXT)", "cast(strftime('%H', receipt_date) AS TEXT)|| ':'|| cast(strftime('%M', receipt_date)/30*30 AS TEXT)", "cast(strftime('%H', receipt_date) AS TEXT)|| ':'|| cast(strftime('%M', receipt_date)/60*60 AS TEXT)", "cast(strftime('%H', receipt_date)/2*2 AS TIME)", "cast(strftime('%H', receipt_date)/4*4 AS TIME)"]
#     selects = ['receipt_items_qty', 'receipt_total_price', 'productsreceipt__qty']
#     date = Receipt.objects.extra(select=({'date_new': times[time]})).order_by('date_new')
#     receipt_select = date.values('date_new', 'receipt_week_day').annotate(sum_total_price=Sum(selects[select]))
#     pandas_select = pd.DataFrame.from_records(receipt_select)
#     data = pandas_select.pivot_table('sum_total_price', index='date_new', columns='receipt_week_day')
#     data = data.rename(columns={'date_new':'Date','receipt_week_day':'Day', 0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'})
#     data['sum'] = data.sum(axis=1)
#     new = pd.DataFrame([data.sum()], index=['sum weeek day'])
#     data = pd.concat([data, new], axis=0)
#     return render_to_response('index.html', {'data': data.to_html()})
