import pandas as pd
import xmltodict
import pyodbc

def get_ramDF(stateCode):
	con = pyodbc.connect('DRIVER={/usr/local/lib/libtdsodbc.so};SERVER={10.209.8.211};DATABASE=pufsandbox;UID=jminneti;PWD=jminneti123;PORT=1433')    
	sql = "SELECT * FROM production.RATING_AREA_MAPPING where state_code = \'"+stateCode+"\'"
    
	return pd.read_sql(sql,con)

def validate(stateCode):
	return get_ramDF(stateCode)