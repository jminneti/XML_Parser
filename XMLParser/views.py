from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django import urls

def homepage(request):
	return render(request, 'homepage.html')