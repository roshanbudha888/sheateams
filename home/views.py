from django.shortcuts import render

# Create your views here.
def shea_home(request):
    return render(request, 'shea_home.html')   # but then home.html would extend base and override the block?

# def home(request):
    # return render(request, 'base.html')   # because base.html has the home content as default.
