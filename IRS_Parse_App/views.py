from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .models import Document
from .forms import DocumentForm
from .tables import UploadsTable

import pandas as pd
import xmltodict
import pyodbc

from .parserHelpers import parse
from .validationHelpers import validate

'''
def IRS_Parse_App_View(request):
	return render(request, 'irsParseTemplate.html')
'''

def IRS_Parse_App_View(request):
	uploadTable = UploadsTable(Document.objects.all())
	form = DocumentForm()

	if request.method == 'POST':		
		if 'upload_button' in request.POST:
			form = DocumentForm(request.POST, request.FILES)
			if form.is_valid():
				form.save()

		if 'delete_button' in request.POST:
		  pks = request.POST.getlist("select")
		  Document.objects.filter(pk__in=pks).delete()
			
	return render(request, 'irsParseTemplate.html', {'form':form, 'uploadTable':uploadTable})

def parse_View(request):
	filePaths = list()
	for doc in Document.objects.all():
		filePaths.append(doc.document.path)

	df = parse(filePaths, debugBit=False)
	
	print(df.head())

	return render(request, 'parseTemplate.html', {'df':df})

def validation_View(request):
	stateCode = 'CA'
	df = validate(stateCode)
	print(df.head())
	return render(request, 'validationTemplate.html')

'''
TODO:
	Story: 
	- Validated data parser
	- Validated DB
	IF cover_entire_state = TRUE, then no zip code data, but it will show duplicates bc NULL

	1) Implement Maple's Rmd Functionality
		- Line 33: Feed list of states
		- Lines 34-37: Store list fo dataframes
		- count(state_code, county, county_name, rating_area_id,
                               plan_id, standard_component_id, age, zip_code, cover_entire_state,
            THIS SHOULD BE ONE
            Problems: CN and MA
            - Mike said that if you open up the list, and go to stateData (list), 
        - print out Line 60:
        	print(paste(state, max(check$n)))
        - print out Lines 34-37: 
        	stateDataList <- list()
			ramDataList <- list()
			diffList <- list()
			checkList <- list()
	2) Add Loading Bar
'''







