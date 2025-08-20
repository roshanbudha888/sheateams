from django.shortcuts import render

# Create your views here.
def rules(request):
    return render(request, 'rule.html')   # note the template name is rule.html