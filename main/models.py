from django.db import models

from django.urls import reverse

from django.contrib.auth.models import User

def upload_path_handler(instance, filename):
    return f"user_{instance.user.pk}/{instance.pk}/{filename}"

def upload_path2_handler(instance, filename):
    return f"user_{instance.user.pk}/{instance.pk}/TrainedDataSet/{filename}"

class DataSet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    algorithm = models.CharField(max_length=30, blank=True, null=True)
    sparkID = models.IntegerField(blank=True, null=True)

    dataSetFile = models.FileField(upload_to=upload_path_handler, blank=True, null=True)

    trainedDataFile = models.FileField(upload_to=upload_path2_handler, blank=True, null=True)


    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sparkID}-{self.algorithm}"

    def get_absolute_url(self):
        return reverse("dataset_details", kwargs={"pk": self.pk})
    

    def get_dataSetFile_url(self):
        return self.dataSetFile.path

    def get_trainedDataSet_url(self):
        return f"/uploads/user_{self.user.pk}/{self.pk}/TrainedDataSet/{self.pk}-{self.algorithm}.zip"
    