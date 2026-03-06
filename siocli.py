# Copyright 2026 Brian Dean
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

from __future__ import division
import argparse
import yaml
import os
import sio_sdk
import siometrics


def persec(var, sec):
    return int(var/sec) if sec > 0 else 0

def stringifyFields(stats):
    #pprint.pprint(stats)
    fields = {}
    for s in stats.keys():
        if s.endswith('Bwc'):
            if 'iops' not in fields.keys(): fields['iops'] = {}
            if 'bw' not in fields.keys(): fields['bw'] = {}
            if 'iosize' not in fields.keys(): fields['iosize'] = {}
            sub = ''
            subm = ''
            if s.endswith('ReadBwc'):
                subm = 'read'
            elif s.endswith('WriteBwc'):
                subm = 'write'
            sub = s[:-len(subm+'Bwc')]
            if subm not in fields['iops'].keys(): fields['iops'][subm] = ''
            if subm not in fields['bw'].keys(): fields['bw'][subm] = ''
            if subm not in fields['iosize'].keys(): fields['iosize'][subm] = ''
            if fields['iops'][subm]: fields['iops'][subm] += ','
            if fields['bw'][subm]: fields['bw'][subm] += ','
            if fields['iosize'][subm]: fields['iosize'][subm] += ','
            fields['iops'][subm] += sub+'='+str(persec(stats[s]['numOccured'],stats[s]['numSeconds']))
            fields['bw'][subm]   += sub+'='+str(persec(stats[s]['totalWeightInKb'],stats[s]['numSeconds']))
            fields['iosize'][subm] += sub+'='+str(stats[s]['totalWeightInKb'] / stats[s]['numOccured'] if stats[s]['totalWeightInKb'] > 0 else 0)
        elif s.endswith('Latency'):
            if 'latency' not in fields.keys(): fields['latency'] = {}
            sub = ''
            subm = ''
            if s.endswith('ReadLatency'):
                subm = 'read'
            elif s.endswith('WriteLatency'):
                subm = 'write'
            sub = s[:-len(subm+'Latency')]
            if subm not in fields['latency'].keys(): fields['latency'][subm] = ''
            if fields['latency'][subm]: fields['latency'][subm] += ','
            fields['latency'][subm] += sub+'='+str(stats[s]['totalWeightInKb'] / stats[s]['numOccured'] if stats[s]['totalWeightInKb'] > 0 else 0)
        else:
            if '' not in fields.keys(): fields[''] = { '': '' }
            if fields['']['']: fields[''][''] += ','
            fields[''][''] += s+'='+str(stats[s])
    return fields

def addMetrics(stype, fields, fmt):
    metrics = []
    for ftype,fvalue in fields.items():
        for fsubtype,fsubvalue in fvalue.items():
            suffix = '.'+ftype if ftype else ''
            suffix += '.'+fsubtype if fsubtype else ''
            metrics.append(  (siometrics.metric[stype]+suffix+','+siometrics.tags[stype]+' '+fsubvalue).format(**fmt) )
    return metrics

def printMetrics(instances, statistics,relations):
    for stype in instances.keys():
        if stype not in statistics : continue
        if stype not in siometrics.metric.keys() : continue
        if stype not in siometrics.tags.keys() : continue
        metrics = []
        fmt = {
            'clu_name': instances['System'][0]['name'] if 'name' in instances['System'][0] and instances['System'][0]['name'] is not None else instances['System'][0]['id'],
            'clu_id' : instances['System'][0]['id']
        }
        if stype == 'System':
            try:
                fields = stringifyFields( statistics[stype] )
                metrics.extend( addMetrics(stype, fields, fmt) )
            except KeyError: continue
        else:
            for obj in instances[stype]:
                if obj['id'] not in statistics[stype]: continue
                try:
                    fmt.update( siometrics.tags_funcs[stype](obj, instances, relations) )
                    fields = stringifyFields( statistics[stype][obj['id']] )
                    metrics.extend( addMetrics(stype, fields, fmt) )
                except KeyError: continue
        for m in metrics:
            print(m)

def main(host, user, passw):
    try:
        sioclient = sio_sdk.SioRestClient(host, user, passw)
        statistics = sio_sdk.collect_statistics(sioclient, os.path.dirname(os.path.abspath(__file__))+'/querySelectedStatistics.json')
        (instances, relations) = sio_sdk.collect_instances(sioclient)
        printMetrics(instances, statistics, relations)
    except sio_sdk.SioRestException as e:
        print(e.message)

if __name__ == "__main__":
    dname = os.path.dirname(os.path.abspath(__file__))
    with open(dname+'/clusters.yaml','r') as infile:
        clusters = yaml.load(infile, Loader=yaml.SafeLoader)
        infile.close()

    parser = argparse.ArgumentParser(description='ScaleIO CLI')
    parser.add_argument('cluster', help='choose a cluster', choices=sorted(clusters.keys()))
    args = parser.parse_args()

    main(clusters[args.cluster]['gateway'], clusters[args.cluster]['username'], clusters[args.cluster]['password'])
