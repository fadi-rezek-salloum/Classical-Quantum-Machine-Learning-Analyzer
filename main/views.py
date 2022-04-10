import pandas as pd

from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView

from pyspark.sql import SparkSession

from .models import DataSet
from .utils import handler, adv_handler
from .forms import TrainingModelForm

@login_required(login_url='/accounts/login/')
def home(request):
    if request.method=='POST':

        dataSetFile = request.FILES.get('dataSetFile')

        instance = DataSet(user=request.user)
        instance.save()

        instance.dataSetFile = dataSetFile
        instance.save()

        spark = SparkSession.builder.master("local[*]").appName('DjangoSparkGP').getOrCreate()
        dataset = instance.get_dataSetFile_url()
        df = spark.read.csv(dataset, header = True, inferSchema = True)

        handler(df, instance.id, instance)

        messages.success(request, 'Dataset has been successfully uploaded and trained')
        
        return HttpResponseRedirect(reverse('dataset_list'))

    context = {}

    return render(request, 'main/home.html', context)


class DataSetList(LoginRequiredMixin, ListView):
    model = DataSet
    template_name = 'main/dataset_list.html'


class DataSetDetail(LoginRequiredMixin, DetailView):
    model = DataSet
    template_name = 'main/dataset_details.html'

    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(DataSet, pk=kwargs.get('pk'))
        csv = pd.read_csv(obj.get_dataSetFile_url())
        df = pd.DataFrame(csv).head(20)

        df = df.to_html()

        context = {
            'df': df,
            'object': obj
        }

        return render(request, self.template_name, context)


@login_required(login_url='/accounts/login/')
def advanced(request):

    form = TrainingModelForm()
    DT = 0
    RFC = 0

    if request.method=='POST':

        form = TrainingModelForm(request.POST, request.FILES)

        dataSetFile = request.FILES['dataSetFile']

        instance = DataSet(user=request.user)
        instance.save()

        instance.dataSetFile = dataSetFile
        instance.save()

        spark = SparkSession.builder.master("local[*]").appName('DjangoSparkGP').getOrCreate()
        dataset = instance.get_dataSetFile_url()
        df = spark.read.csv(dataset, header = True, inferSchema = True)

        if form.is_valid():
            DT = form.cleaned_data['DT']
            RFC = form.cleaned_data['RFC']
            min_depth = form.cleaned_data['min_depth']
            max_depth = form.cleaned_data['max_depth']

            adv_handler(df=df, id=instance.id, RFC=RFC, DT=DT, max_depth=[min_depth, max_depth], instance=instance)

            messages.success(request, 'Dataset has been successfully uploaded and trained')
        
            return HttpResponseRedirect(reverse('dataset_list'))

    context = {
        'form': form,
    }

    return render(request, 'main/advanced.html', context=context)
