import numpy as np
from keras.models import load_model
# Load the saved model
import datetime
def predict(fil):
    model = load_model('8_8min.keras')
    X_new = fil
    X=np.array(X_new)
    Y=X[:,-1]
    X=X[:,:-1]
    predictions = model.predict(X)
    predicted_classes = np.argmax(predictions, axis=1)
    for x,y in zip(predicted_classes,Y):
        unix_timestamp = y
        dt_object = datetime.datetime.fromtimestamp(unix_timestamp)
        y = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        print(y,x)