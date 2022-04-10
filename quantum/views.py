from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .utils import read_file, train_and_test

@login_required(login_url='/accounts/login/')
def quantum(request):

    if request.method=='POST':

        dataSetFile = request.FILES.get('dataSetFile')

        X = int(request.POST.get('X'))
        Y = int(request.POST.get('Y'))
        Z = int(request.POST.get('Z'))

        data = read_file(dataSetFile)

        chart = train_and_test(data, repetitions = [X, Y, Z])

        request.session['chart'] = chart
        return redirect(reverse('result'))

    context = {}

    return render(request, 'quantum/quantum.html', context)


def result(request, *args, **kwargs):

    context = {
    }

    return render(request, 'quantum/result.html', context)