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

################# FUNCTIONS #################

def fmt_Sds(sds, instances, relations):
    parent = None
    for pdo in instances['ProtectionDomain']:
        if pdo['id'] in relations['parents'][sds['id']]['ProtectionDomain']:
            parent = pdo
            break
    if parent is None:
        raise Exception('Parent not found')
    return { 'sds_name': sds['name'].replace('=','\\='), 'sds_id': sds['id'].replace('=','\\='),
             'pdo_name': parent['name'].replace('=','\\='), 'pdo_id': parent['id'].replace('=','\\=') }

def fmt_Device(device, instances, relations):
    parentSDS = None
    parentSTO = None
    parentPDO = None
    for sds in instances['Sds']:
        if sds['id'] in relations['parents'][device['id']]['Sds']:
            parentSDS = sds
            break
    for sto in instances['StoragePool']:
        if sto['id'] in relations['parents'][device['id']]['StoragePool']:
            parentSTO = sto
            break
    for pdo in instances['ProtectionDomain']:
        if pdo['id'] in relations['parents'][parentSTO['id']]['ProtectionDomain']:
            parentPDO = pdo
            break
    if parentSDS is None or parentSTO is None or parentPDO is None:
        raise Exception('Parent not found')
    
    dev_id = device['id'].replace('=','\\=')
    dev_name = device['name'].replace('=','\\=') if device['name'] is not None else dev_id

    sds_id = parentSDS['id'].replace('=','\\=')
    sds_name = parentSDS['name'].replace('=','\\=') if parentSDS['name'] is not None else sds_id

    sto_id = parentSTO['id'].replace('=','\\=')
    sto_name = parentSTO['name'].replace('=','\\=') if parentSTO['name'] is not None else sto_id

    pdo_id = parentPDO['id'].replace('=','\\=')
    pdo_name = parentPDO['name'].replace('=','\\=') if parentPDO['name'] is not None else pdo_id

    dev_path = device['deviceCurrentPathName'].replace('/dev/','',1).replace('=','\\=')

    return { 'dev_name': dev_name, 'dev_id': dev_id,
             'dev_path': dev_path,
             'sds_name': sds_name, 'sds_id': sds_id,
             'sto_name': sto_name, 'sto_id': sto_id,
             'pdo_name': pdo_name, 'pdo_id': pdo_id }

def fmt_Volume(volume, instances, relations):
    parentSTO = None
    parentPDO = None
    for sto in instances['StoragePool']:
        if sto['id'] in relations['parents'][volume['id']]['StoragePool']:
            parentSTO = sto
            break
    for pdo in instances['ProtectionDomain']:
        if pdo['id'] in relations['parents'][parentSTO['id']]['ProtectionDomain']:
            parentPDO = pdo
            break
    if parentSTO is None or parentPDO is None:
        raise Exception('Parent not found')

    vol_id = volume['id'].replace('=','\\=')
    vol_name = volume['name'].replace('=','\\=') if volume['name'] is not None else vol_id

    sto_id = parentSTO['id'].replace('=','\\=')
    sto_name = parentSTO['name'].replace('=','\\=') if parentSTO['name'] is not None else sto_id

    pdo_id = parentPDO['id'].replace('=','\\=')
    pdo_name = parentPDO['name'].replace('=','\\=') if parentPDO['name'] is not None else pdo_id

    return { 'vol_name': vol_name, 'vol_id': vol_id,
             'sto_name': sto_name, 'sto_id': sto_id,
             'pdo_name': pdo_name, 'pdo_id': pdo_id }

def fmt_StoragePool(pool, instances, relations):
    parent = None
    for pdo in instances['ProtectionDomain']:
        if pdo['id'] in relations['parents'][pool['id']]['ProtectionDomain']:
            parent = pdo
            break
    if parent is None:
        raise Exception('Parent not found')
    
    sto_id = pool['id'].replace('=','\\=')
    sto_name = pool['name'].replace('=','\\=') if pool['name'] is not None else sto_id

    pdo_id = parent['id'].replace('=','\\=')
    pdo_name = parent['name'].replace('=','\\=') if parent['name'] is not None else pdo_id

    return { 'sto_name': sto_name, 'sto_id': sto_id,
             'pdo_name': pdo_name, 'pdo_id': pdo_id }

def fmt_Sdc(sdc, instances, relations):
    name = sdc['name'] if sdc['name'] is not None else sdc['sdcIp']
    return { 'sdc_name': name.replace('=','\\='), 'sdc_id': sdc['id'].replace('=','\\=') }

def fmt_ProtectionDomain(domain, instances, relations):
    pdo_id = domain['id']
    pdo_name = domain['name'].replace('=','\\=') if domain['name'] is not None else pdo_id

    return { 'pdo_name': pdo_name, 'pdo_id': pdo_id}

################# VARIABLES #################

tags = {
    'System'           : 'cluster={clu_name},cluster_id={clu_id}',
    'Sds'              : 'cluster={clu_name},cluster_id={clu_id},sds={sds_name},sds_id={sds_id},protection_domain_id={pdo_id},protection_domain_name={pdo_name}',
    'Device'           : 'cluster={clu_name},cluster_id={clu_id},sds={sds_name},sds_id={sds_id},device_name={dev_name},device_id={dev_id},device_path={dev_path},storage_pool_id={sto_id},storage_pool_name={sto_name},protection_domain_id={pdo_id},protection_domain_name={pdo_name}',
    'Volume'           : 'cluster={clu_name},cluster_id={clu_id},volume_name={vol_name},volume_id={vol_id},storage_pool_id={sto_id},storage_pool_name={sto_name},protection_domain_id={pdo_id},protection_domain_name={pdo_name}',
    'StoragePool'      : 'cluster={clu_name},cluster_id={clu_id},storage_pool_id={sto_id},storage_pool_name={sto_name},protection_domain_id={pdo_id},protection_domain_name={pdo_name}',
    'Sdc'              : 'cluster={clu_name},cluster_id={clu_id},sdc_name={sdc_name},sdc_id={sdc_id}',
    'ProtectionDomain' : 'cluster={clu_name},cluster_id={clu_id},protection_domain_id={pdo_id},protection_domain_name={pdo_name}'
}

metric = {
    'System'           : 'scaleio.cluster',
    'Sds'              : 'scaleio.sds',
    'Device'           : 'scaleio.device',
    'Volume'           : 'scaleio.volume',
    'StoragePool'      : 'scaleio.storagepool',
    'Sdc'              : 'scaleio.sdc',
    'ProtectionDomain' : 'scaleio.protectiondomain'
}

tags_funcs = {
    'Sds'              : fmt_Sds,
    'Device'           : fmt_Device,
    'Volume'           : fmt_Volume,
    'StoragePool'      : fmt_StoragePool,
    'Sdc'              : fmt_Sdc,
    'ProtectionDomain' : fmt_ProtectionDomain
}
