from django.shortcuts import render

# Create your views here.
def analisis_home(request):
  return render(request, 'analysis/analysis.html')