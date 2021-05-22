
from django.shortcuts import render
def index(request):
    welcome=(request.session.get("fname"))
    return render(request, 'index.html',{"welcome":welcome})