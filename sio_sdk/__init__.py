# Copyright 2026 Dell, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import sys
import json
import time
from sio_sdk.SioSdk import SioRestClient
from sio_sdk.SioSdk import SioRestException
from sio_sdk.SioSdk import err

def collect_instances(sio_rest_client):
    instances = {}
    relations = {'children':{}, 'parents':{}}
    alldata = sio_rest_client.get_json('/api/instances')
    for siotype, sioobjs in alldata.items():
        if siotype == 'System' or siotype.endswith('List'):
            sio_type = siotype[0].upper()+siotype[1:].replace('List','')
            instances[sio_type] = []
            if sioobjs:
                if siotype == 'System':
                    instances[sio_type].append(sioobjs)
                else:
                    instances[sio_type].extend(sioobjs)
                for sio_obj in instances[sio_type]:
                    for sio_obj_link in sio_obj['links']:
                        if  sio_obj_link['rel'].startswith('/api/parent'):
                            link_type = sio_obj_link['href'].split(':')[0].split('/')[-1]
                            link_id = sio_obj_link['href'].split(':')[-1]
                            if link_id not in relations['children']:
                                relations['children'][link_id] = {}
                            if sio_type not in relations['children'][link_id]:
                                relations['children'][link_id][sio_type] = []
                            if sio_obj['id'] not in relations['parents']:
                                relations['parents'][sio_obj['id']] = {}
                            if link_type not in relations['parents'][sio_obj['id']]:
                                relations['parents'][sio_obj['id']][link_type] = []
                            relations['children'][link_id][sio_type].append(sio_obj['id'])
                            relations['parents'][sio_obj['id']][link_type].append(link_id)
    return (instances, relations)

def collect_statistics(sio_rest_client, json_file):
#    """
#        Send JSON file to .../api/instances/querySelectedStatistics URI
#        Return the JSON parsed object
#    """
    with open(json_file) as data_file:
        return sio_rest_client.post_json('/api/instances/querySelectedStatistics',
                                         json.load(data_file))

def collect_sds(sio_rest_client, extractFunc=None):
#    """
#        Collect all SDS details.
#        We can filter the results by using the 'extractFunc' parameter, i.e. :
#           collect_sds( sio_rest_client, lambda x: {'ipList': x['ipList'], 'name': x['name'], 'id': x['id']} )
#           will return only IPs, name, and id.
#    """
    alldata = sio_rest_client.get_json('/api/types/Sds/instances')
    if extractFunc :
        return list(map(extractFunc, alldata))
    return alldata

def st_time(func):
    """
        Function decorator to calculate duration
    """
    def st_func(*args, **keyArgs):
        """
            Execute decorated function between two time collection.
        """
        stime = time.time()
        result = func(*args, **keyArgs)
        err("Function=%s, Time=%s" % (func.__name__, time.time() - stime))
        return result
    return st_func
