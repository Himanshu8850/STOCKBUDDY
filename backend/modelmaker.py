import numpy as np 
import json
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
import pandas as pd
import datetime
from sklearn.utils import resample
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Dropout, BatchNormalization
from keras.optimizers import RMSprop
import maker

def train(fil):
    al = np.loadtxt(f'{fil}')
    al=al[:,1:]
    print(al.shape)
    # np.random.seed(1234)
    # np.random.shuffle(al)
    lim= len(al)
    l=int(lim/10)
    lim-=l
    lim+=l%2
    X_train, Y_train = al[:lim, :-1], al[:lim, -1]
    X_test, Y_test = al[lim:, :-1], al[lim:, -1]
    label_mapping = {-1: 0, 0: 0, 1: 1}
    Y_train = np.array([label_mapping[label] for label in Y_train])
    Y_test = np.array([label_mapping[label] for label in Y_test])

    # Split test data into validation and test sets
    X_test, X_validation = np.split(X_test, 2)
    Y_test, Y_validation = np.split(to_categorical(Y_test, 2), 2)

    # Convert Y_train to one-hot encoding
    Y_train = to_categorical(Y_train, 2)

    # Define the model architecture
    model = Sequential()
    model.add(BatchNormalization(input_shape=(X_train.shape[1],)))  # Ensure input shape matches your data
    model.add(Dense(1000, activation='relu', kernel_initializer='he_normal'))
#     model.add(Dropout(0.2))
    model.add(BatchNormalization())
    model.add(Dense(450, activation='relu', kernel_initializer='he_normal'))
    # model.add(Dropout(0.1))
    model.add(BatchNormalization())
    model.add(Dense(150, activation='relu', kernel_initializer='he_normal'))
    model.add(BatchNormalization())
    model.add(Dense(2, activation='softmax'))  # Output layer with 2 units for binary classification

    # Compile the model
    model.compile(loss='categorical_crossentropy', optimizer=RMSprop(learning_rate=0.001), metrics=['accuracy'])

    # Print model summary to review architecture and number of parameters
    print(model.summary())

    # Train the model
    history = model.fit(X_train, Y_train, validation_data=(X_validation, Y_validation), epochs=200, batch_size=72)
    # Evaluate the model on test data
    loss, accuracy = model.evaluate(X_test, Y_test)
    print(f'Test loss: {loss:.4f}, Test accuracy: {accuracy:.4f}')
    fil=fil.split('.txt')
    fil=''.join(fil)
    model.save(f'{fil}.keras')
    return accuracy
# /////////////////////////////////////////////////////////////

# /////////////////////////////////////////////////////////////

# /////////////////////////////////////////////////////////////

# /////////////////////////////////////////////////////////////


tr=12
fut=12
maker.compute_features(tr,fut,"tr")
maker.compute_features(tr,fut,"t")

data=pd.read_csv('trainn .csv')
# with open('/kaggle/input/finall/ticks.csv') as f:
#     d = json.load(f)
#     # print(d['candles'])
#     data=[x for x in d['candles']]
# Function to zero out year, day, and seconds, keeping only hours and minutes
# def transform_timestamp(timestamp):
#     dt = datetime.datetime.utcfromtimestamp(timestamp)
#     # Create a new datetime object with zeroed out year, month, day and seconds
#     new_dt = datetime.datetime(1970, 1, 1, dt.hour, dt.minute)
#     # Convert back to Unix timestamp
#     new_timestamp = int(new_dt.timestamp())
#     day=dt.weekday()
#     return new_timestamp,day

# Apply the transformation
# transformed_times = np.array([transform_timestamp(ts) for ts in data[:, 0]])

# Replace the time column with the transformed times
# data = np.hstack((transformed_times, data[:, 1:]))
data=np.array(data)
data=data[1:]
print(data[:2])
# tr=5
maxi=-1
besttr=-1



# for tr in range(30,45,2):
# l =  [odata[z-tr:z].flatten() for z in range(past, len(odata))]
# l=np.array(l)
# l=l[:-fut]
future=data[:,-1]


# momentum=[]
# for i in range(past-1,len(odata)-fut-1):
#     pos = (data[i+z,5]-data[i,5])
#     momentum.append(pos)
#     pos=np.sum([((data[i+z,5]-data[i,5])/data[i,5])>=0.03 for z in range(fut+1)])
#     neg=np.sum([((data[i+z,5]-data[i,5])/data[i,5])<=-0.03 for z in range(fut+1)])
#     if pos>neg: future.append(1)
#     elif neg>pos: future.append(-1)
#     else: future.append(0)


# l=np.array(l)
# l = np.column_stack((l,momentum))
# l=scaler.fit_transform(l)
# l = np.column_stack((l,future))
print(np.sum([f==1 for f in future]),tr,data.shape[0])
# np.random.seed(1234)
# np.random.shuffle(l)



df =pd.DataFrame(data)
class_column = -1
max_count = df.iloc[:, class_column].value_counts().max()

# Create an empty DataFrame to store the resampled data
resampled_df = pd.DataFrame()

# Upsample each class to the maximum count
for class_label in df.iloc[:, class_column].unique():
    class_subset = df[df.iloc[:, class_column] == class_label]
    resampled_class_subset = resample(class_subset, 
                                      replace=True,  # Sample with replacement
                                      n_samples=max_count,  # Match max class count
                                      random_state=42)  # For reproducibility
    resampled_df = pd.concat([resampled_df, resampled_class_subset])

# Shuffle the resampled DataFrame
resampled_df = resampled_df.sample(frac=1, random_state=42).reset_index(drop=True)
print(resampled_df.iloc[:, class_column].value_counts())
np.savetxt(f'{tr}_{fut}min.txt', resampled_df, fmt='%.18e')

accuracy=train(f'{tr}_{fut}min.txt')
if maxi<accuracy:
    maxi=accuracy
besttr=tr
print("best tr is:",maxi,besttr)
    