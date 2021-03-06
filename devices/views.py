from django.shortcuts import render

import json
from bson import ObjectId
from pymongo import MongoClient
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import datetime

import logging
logger = logging.getLogger('django')
db_conf = settings.DATABASES['default']
client = MongoClient(db_conf['HOST'], int(db_conf['PORT']))
db = eval("client.{0}".format(db_conf['NAME']))

def ap(request):
    result = {}
    if request.method == 'GET' :
        data = []

        showValue = ['name','floor','height','address','longitude','latitude','status']
        showValueDict = {}
        for i in showValue:
            showValueDict[i] = 1
        for out in db.accesspoint.find({},showValueDict):
            o_id = out['_id'].__str__()
            out['_id'] = o_id
            data.append(out)

        result['status'] = 'ok'
        result['data'] = data
        return HttpResponse(json.dumps(result,encoding='utf8',indent=4), content_type="application/json")
    elif request.method == 'PUT' :
        try:
            body_data_list = json.loads(request.body)

            #if type(body) != type([]):
            #    return HttpResponse(json.dumps(
            #    {'status': 'Failed', 'Info': 'Request body is not valid list. plz check again', 'Data': request.body},
            #    indent=4), content_type="application/json")

        except Exception, e:
            #logger.debug('[1]---{0}---{1}---{2}'.format(Exception, e, request.body))
            print
            return HttpResponse(json.dumps(
                {'status': 'Failed', 'Info': '%s-%s' % (Exception,e), 'Data': request.body},
                indent=4), content_type="application/json")

        ap = db.accesspoint
        now = datetime.datetime.now()
        current = {}

        for i in body_data_list:
            try:
                current = i
                current['update_by'] = 'API'
                current['update_on'] = now
                res = ap.update({'_id': ObjectId(current['id'])},{'$set': current})
                if res['ok'] != 1 or res['nModified']!=1 :
                    logger.debug('[ERROR]-----cannot insert :{0}---{1}---{2}'.format(res,current['id'], current))
                    if not result.has_key('ERROR'):
                        result['ERROR'] = []
                    result['ERROR'].append(current['id'])

            except Exception, e:
                if not result.has_key('ERROR'):
                    result['ERROR'] = []
                result['ERROR'].append(
                    {'id': current['id'], "content": json.dumps(current), "exception": '[{0}]'.format(e)})
        result['status'] = 'ok'
        return HttpResponse(json.dumps(result,encoding='utf8', indent=4), content_type="application/json")


