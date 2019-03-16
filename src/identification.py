from keras.models import Sequential
from keras.layers import Dense, Activation
import keras
from sklearn.model_selection import StratifiedKFold
from sklearn import preprocessing
import numpy as np


def perform_identification(x_set, y_set):
    file = open("repeated_results.csv", "w")
    file.write('lr,mom,acc\n')
    print "Data preprocessing"
    le = preprocessing.LabelEncoder()
    y_set = le.fit_transform(y_set)
    classes_count = len(le.classes_)
    print "Number of users: {0}".format(classes_count)

    x_set_normalized = preprocessing.maxabs_scale(x_set)
    skf = StratifiedKFold(n_splits=5)

    for R in range(10):
        print "Starting model evaluation"
        for lr in [ 0.01]:
            for mom in [0.9]:
                print "LR: {0}, MOM: {1}".format(lr, mom)
                i = 0
                results = np.array([])
                for train, test in skf.split(x_set_normalized, y_set):
                    print "K-FOLD iteration: {0}".format(i)
                    i += 1
                    model = sequential_model(classes_count, lr, mom)
                    x_train = x_set_normalized[train]
                    x_test = x_set_normalized[test]
                    y_train = keras.utils.to_categorical(y_set[train], classes_count)
                    y_test = keras.utils.to_categorical(y_set[test], classes_count)
                    metrics = train_and_evaluate_model(x_train, y_train, x_test, y_test, model)
                    if len(results) == 0:
                        results = np.array(metrics)
                    else:
                        results = np.vstack([results, np.array(metrics)])

                results = np.mean(results, axis=0)
                file.write("{0},{1},{2}\n".format(lr, mom, results[1]))
                print '======================'
                print "MEAN ACC: {0}".format(results[1])
                print '======================'

    file.close()


def train_and_evaluate_model(x_train, y_train, x_test, y_test, model):
    model.fit(x_train, y_train, epochs=200, batch_size=32, verbose=1)
    loss_and_metrics = model.evaluate(x_test, y_test, batch_size=128)

    return loss_and_metrics


def sequential_model(output_classes_count, lr, mom):
    model = Sequential()

    model.add(Dense(units=64, input_dim=24))
    model.add(Activation('relu'))
    model.add(Dense(units=64))
    model.add(Activation('relu'))
    model.add(Dense(units=output_classes_count))
    model.add(Activation('softmax'))

    # model.compile(loss='categorical_crossentropy',
    #               optimizer='sgd',
    #               metrics=['accuracy'])

    model.compile(loss=keras.losses.categorical_crossentropy,
                  optimizer=keras.optimizers.SGD(lr=lr, momentum=mom, nesterov=True),
                  metrics=['accuracy'])

    return model
