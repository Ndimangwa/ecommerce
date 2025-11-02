from django.shortcuts import render

# Create your views here.
def not_allowed(request):
    return render(request, 'not_allowed.html', {})