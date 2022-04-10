import os
import pyspark
import pandas as pd
import zipfile

from pyspark.ml.feature import StringIndexer, VectorAssembler, OneHotEncoder
from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))


def encode_data(df, id=0):
    categoricalColumns = []
    stages = []

    for categoricalCol in categoricalColumns:
        stringIndexer = StringIndexer(inputCol = categoricalCol, outputCol = categoricalCol + 'Index')
        encoder = OneHotEncoder(inputCols=[stringIndexer.getOutputCol()], outputCols=[categoricalCol + "classVec"])
        stages += [stringIndexer, encoder]

    label_column = df.columns[-1]
    label_stringIdx = StringIndexer(inputCol = label_column, outputCol = 'label')

    stages += [label_stringIdx]

    numericCols = df.columns[:-1]

    assemblerInputs = [c + "classVec" for c in categoricalColumns] + numericCols
    assembler = VectorAssembler(inputCols=assemblerInputs, outputCol="features")
    stages += [assembler]

    pipeline = Pipeline(stages = stages)
    pipelineModel = pipeline.fit(df)
    df = pipelineModel.transform(df)
    selectedCols = ['label', 'features']
    df = df.select(selectedCols)

    train_main, test_main = df.randomSplit([0.9, 0.1], seed = 2018)
    train_secondary,test_secondary = test_main.randomSplit([0.9, 0.1], seed = 2021)

    return train_main, test_main, train_secondary, test_secondary


def decision_tree(train, test, id=0, save_flag=0, max_depth=3, instance={}):

            dt = DecisionTreeClassifier(featuresCol = 'features', labelCol = 'label', maxDepth = max_depth)
            dtModel = dt.fit(train)
            predictions = dtModel.transform(test)

            if save_flag:
                dtModel.save(f'./uploads/user_{instance.user.id}/{id}/TrainedDataSet/{id}-DT')
                zipf = zipfile.ZipFile(f'./uploads/user_{instance.user.id}/{id}/TrainedDataSet/{id}-DT.zip', 'w', zipfile.ZIP_DEFLATED)
                zipdir(f'./uploads/user_{instance.user.id}/{id}/TrainedDataSet/{id}-DT', zipf)
                zipf.close()
                instance.trainedDataFile = zipf.filename
                instance.algorithm = "DT"
                instance.sparkID = id
                instance.save()

            evaluator = BinaryClassificationEvaluator()

            return id, str(evaluator.evaluate(predictions, {evaluator.metricName: "areaUnderROC"}))



def random_forest(train, test, id=0, save_flag=0, instance={}):

    rf = RandomForestClassifier(featuresCol = 'features', labelCol = 'label')
    rfModel = rf.fit(train)
    predictions = rfModel.transform(test)

    if save_flag:
        rfModel.save(f'./uploads/user_{instance.user.id}/{id}/TrainedDataSet/{id}-RFC')
        zipf = zipfile.ZipFile(f'./uploads/user_{instance.user.id}/{id}/TrainedDataSet/{id}-RFC.zip', 'w', zipfile.ZIP_DEFLATED)
        zipdir(f'./uploads/user_{instance.user.id}/{id}/TrainedDataSet/{id}-RFC', zipf)
        zipf.close()
        instance.trainedDataFile = zipf.filename
        instance.algorithm = "RFC"
        instance.sparkID = id
        instance.save()

    evaluator = BinaryClassificationEvaluator()

    return id,str(evaluator.evaluate(predictions, {evaluator.metricName: "areaUnderROC"}))



def decision_model(train, test, dt_max_depth = [3,6], id=0):
    dt_depth_list = []
    dt_ROC_list = []

    for depth in range(dt_max_depth[0], dt_max_depth[1] + 1):
        id0, ROC0 = decision_tree(train, test, id, 0, depth)
        dt_depth_list.append(depth)
        dt_ROC_list.append(ROC0)
    try :
        OC0 = max(dt_ROC_list)
    except  :
        ROC0 = 0
    try:
        dt_best_depth = dt_depth_list(dt_ROC_list.index(ROC0))
    except :
        dt_best_depth = 3
    id1, ROC1 = random_forest(train, test, id, 0)

    if id==id0 and id==id1:
        if ROC0>ROC1:
            return 0, dt_best_depth
        else:
            return 1, 0
    else:
        raise ValueError('Error !')
    


def handler(df, id=0, max_depth=[3, 6], instance={}):
    train_main, test_main, train_secondary, test_secondary = encode_data(df)
    best_model, dt_best_depth = decision_model(train_secondary, test_secondary, max_depth, id)

    if best_model == 0:
        decision_tree(train_main, test_main, id, 1, dt_best_depth, instance)
    elif best_model == 1:
        random_forest(train_main, test_main, id, 1, instance)



def adv_handler(df, id = 0, RFC = 0, DT = 0, max_depth=[3,6], instance={}):

    if RFC and DT :
        handler(df, id, max_depth, instance)
    else :
        train_main, test_main,train_secondary,test_secondary = encode_data(df)
        if RFC :
            random_forest(train_main, test_main, id, 1, instance)
        elif DT:
            dt_depth_list = []
            dt_ROC_list = []
            for depth in range(max_depth[0],max_depth[1]+1):
                id0, ROC0 = decision_tree(train_main, test_main, id, 0, depth)
                dt_depth_list.append(depth)
                dt_ROC_list.append(ROC0)
            try :
                ROC0 = max(dt_ROC_list)
            except  :
                ROC0 = 0
            try:
                dt_best_depth = dt_depth_list[dt_ROC_list.index(ROC0)]
            except :
                dt_best_depth = 6
            decision_tree(train_main, test_main, id, 1, dt_best_depth, instance)