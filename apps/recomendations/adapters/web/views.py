from django.shortcuts import render

# Create your views here.
def recomendations(request):
    return render(request, 'analysis/recommendation.html')