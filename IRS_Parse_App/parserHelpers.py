'''
For the following counties:
    CA: Inyo, Mono, Monterey, San Benito, San Luis Obispo, and Santa Barbara
    WA: Chelan, Douglas, Ferry, Lincoln, Pend Oreille, Skamania, and Stevens

Validate that these counties don't have plans for the following:

    - PP.market_coverage LIKE '%Individual%' -- individual only plans only
    - PP.dental_only_plan = 'No'
    - PP.metal_level = 'Bronze'
    - PP.qhp_non_qhp_type_id != 'Off the Exchange'
    - PP.business_year = '2018'
    - PP.state_code = 'CA'
    - PS.county_name = 'Mono'
    - PP.child_only_offering != 'Allows Child-Only'
    - --AND PS.cover_entire_state = 'true' 
    - PP.plan_id_code like '%01%'
    - PR.age = '21' or 'Family Option'     
    
'''

import pandas as pd
import xmltodict
import pyodbc

#%% Let's grab the XMLs we need

def importXML(filePaths):
    rawXML = dict()
    
    for path in filePaths:
        fileName = path.split('/')[-1] 
        stateCode = fileName.split('_')[0]
        if stateCode not in rawXML.keys():
            rawXML[stateCode] = dict()
            
        name = (fileName.split('_')[1]).split('.')[0]

        with open(path) as fd:
            rawXML[stateCode][name] = xmltodict.parse(fd.read())
    
    return rawXML


# Connect to DB and grab county name-number map
def get_ramDF():
    con = pyodbc.connect('DRIVER={/usr/local/lib/libtdsodbc.so};SERVER={10.209.8.211};DATABASE=pufsandbox;UID=jminneti;PWD=jminneti123;PORT=1433')
    
    sql = '''
            SELECT *
            FROM production.RATING_AREA_MAPPING
            where state_code = 'CA' or state_code = 'WA' or state_code = 'NY'
          '''
    
    return pd.read_sql(sql,con)


# Converter function, gets county number given a county name
def getCountyNum(stateCode, countyName, ramDF):
    return str(ramDF.loc[(ramDF['state_code']==stateCode) & (ramDF['county_name']==countyName)]['county'].iloc[0]).zfill(3)

# Generate sk_ps
'''
Need to link from ServiceAreas to Plan using
    - asOfDate
    - stateCode
    - issuerId
    - serviceAreaId
'''
def getAll_sk_ps(stateCode, countyName, ramDF, rawXML):
    countyNum = getCountyNum(stateCode, countyName, ramDF)
    results = list()
    asOfDate = rawXML[stateCode]['ServiceArea']['pufServiceArea']['@asOfDate']
    for issuer in rawXML[stateCode]['ServiceArea']['pufServiceArea']['issuer']:
        issuerId = issuer['issuerId']
        for serviceArea in issuer['serviceArea']:
            try:                
                if (serviceArea['county'] == countyNum):
                    results.append({'asOfDate'      : asOfDate,
                                    'stateCode'     : stateCode,
                                    'issuerId'      : issuerId,
                                    'serviceAreaId' : serviceArea['serviceAreaId'],
                                    'county'        : serviceArea['county']})
            except TypeError as err:
                continue
    return results


# Pull Plan data for sk_ps
def getPlans(sk_ps, rawXML, countyName):
    results = list()

    for sk in sk_ps:
        if type(sk) == str:
            sk = sk_ps
        stateCode = sk['stateCode']
        for issuer in rawXML[stateCode]['Plans']['pufPlans']['issuer']:
            try:
                if issuer['issuerId'] != sk['issuerId']:
                    continue
            except TypeError as err:
                continue
                    
            else:                
                for plan in issuer['plans']['plan']:
                    if type(plan) == str:
                        plan = issuer['plans']['plan']
                        
                    if plan['serviceAreaId'] == sk['serviceAreaId']:
                        marketCoverage = plan['marketCoverage']
                        dentalOnlyPlan = plan['dentalOnlyPlan']
                        metalLevel = plan['metalLevel']
                        qhpNonQhpTypeId = plan['qhpNonQHPTypeId']
                        childOnlyOffering = plan['childOnlyOffering']

                        for costShareVariant in plan['costShareVariances']['costShareVariant']:                                
                            if(type(costShareVariant) == str):
                                costShareVariant = plan['costShareVariances']['costShareVariant']
                                
                            if 'planId' in costShareVariant.keys():
                                planId = costShareVariant['planId']
                                results.append({'asOfDate'             : sk['asOfDate'],
                                                'stateCode'            : stateCode,
                                                'countyName'           : countyName,
                                                'countyNum'            : sk['county'],
                                                'serciceAreaId'        : sk['serviceAreaId'],
                                                'marketCoverage'       : marketCoverage,
                                                'dentalOnlyPlan'       : dentalOnlyPlan,
                                                'metalLevel'           : metalLevel,
                                                'qhpNonQhpTypeId'      : qhpNonQhpTypeId,
                                                'childOnlyOffering'    : childOnlyOffering,
                                                'planId'               : planId})
                    
    return results

'''------------------------------------------------------------------------------------------------------------------------------------------------------ 
parse(filePaths)
Perform our parsing

Returns dataframe of results
'''
def parse(filePaths, debugBit):
    if debugBit:
        print('File Paths: ' + str(filePaths))

    rawXML = importXML(filePaths)
    ramDF = get_ramDF()
    counties = {'CA': ['Inyo', 'Mono', 'Monterey', 'San Benito', 'San Luis Obispo', 'Santa Barbara'],
                'WA': ['Chelan', 'Douglas', 'Ferry', 'Lincoln', 'Pend Oreille', 'Skamania', 'Stevens'],
                'NY': ['Bronx', 'Albany']} 
    df = None
    uniqueList = list()
    for stateCode, countyList in counties.items():
        if stateCode not in rawXML.keys():
            continue
        for countyName in countyList:
            sk_ps = getAll_sk_ps(stateCode, countyName, ramDF, rawXML)
            results = getPlans(sk_ps, rawXML, countyName)                                
            df = pd.DataFrame(data=results)

            unique_metalLevel = sorted(df['metalLevel'].unique())
            unique_dentalOnlyPlan =sorted(df['dentalOnlyPlan'].unique())
            bronzeAndNo = ('Bronze' in unique_metalLevel) and ('No' in unique_dentalOnlyPlan)

            uniqueList.append({ '1stateCode'                 : stateCode,
                                '2countyName'                : countyName,
                                '3unique_dentalOnlyPlan'     : unique_metalLevel,
                                '4unique_metalLevel'         : unique_dentalOnlyPlan,
                                '5bronzeAndNo'               : bronzeAndNo
                                })
            '''
            print('\nFor ' +stateCode+', '+countyName)
            print('Unique Metals: '+str(df['metalLevel'].unique()))
            print('Unique Dental: '+str(df['dentalOnlyPlan'].unique()))
            '''


    return pd.DataFrame(data=uniqueList)
