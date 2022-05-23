import os
import tensorflow as tf
import numpy as np
from werkzeug.utils import secure_filename
from apiflask.fields import File
from apiflask import APIFlask, Schema
from flask_cors import CORS

app = APIFlask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get('/')
def say_hello():
    print(UPLOAD_FOLDER)
    # returning a dict equals to use jsonify()
    return {'message': 'Hello!'}


class ImageSchema(Schema):
    image = File(validate=lambda f: f.mimetype in ['image/jpeg', 'image/png'])

@app.post('/predict')
@app.input(ImageSchema, location='files')
def upload_image(data):
    f = data['image']

    print(f.filename)

    filename = secure_filename(f.filename)
    f.save(os.path.join(UPLOAD_FOLDER, filename))
    class_names = ['cbb', 'cbsd', 'cgm', 'cmd', 'healthy']
    model_test = tf.keras.models.load_model('/usr/src/app/my_model.h5')

    img = tf.keras.utils.load_img(
        f'{UPLOAD_FOLDER}/{filename}', target_size=(256, 256)
    )
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch

    predictions = model_test.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    if os.path.exists('/'.join([UPLOAD_FOLDER, filename])):
        os.remove('/'.join([UPLOAD_FOLDER, filename]))

    return {'message': "This image most likely belongs to {} with a {:.2f} percent confidence."
        .format(class_names[np.argmax(score)], 100 * np.max(score))}, 200


if __name__ == '__main__':
    app.run()
