from django.db import models

class countyResults(models.Model):
	stateCode = models.CharField(max_length=500)
	countyName = models.CharField(max_length=500)
	countyNum = models.CharField(max_length=500)
	uniqueMetalLevels = models.CharField(max_length=500)
	uniqueDentalOnly = models.CharField(max_length=500)

class Document(models.Model):    
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)