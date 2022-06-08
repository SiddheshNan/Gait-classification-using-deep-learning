import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import tensorflow.keras.datasets.mnist as ModelData


data = []
labels = ['back', 'front', 'normal']

INIT_LR = 1e-4
EPOCHS = 20
BS = 4

back = open("training/back.txt", "r").readlines()
front = open("training/front.txt", "r").readlines()
normal = open("training/normal.txt", "r").readlines()


def addData(data1, myData):
    db = data1.load_data()
    arr = [myData, db, labels]
    data1 = arr


addData(ModelData, back)
addData(ModelData, front)
addData(ModelData, normal)

(x_train, y_train), (x_test, y_test) = ModelData.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(10)
])
predictions = model(x_train[:1]).numpy()
tf.nn.softmax(predictions).numpy()
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
loss_fn(y_train[:1], predictions).numpy()

model.compile(optimizer='adam',
              loss=loss_fn,
              metrics=['accuracy'])
model.fit(x_train, y_train, epochs=5)
