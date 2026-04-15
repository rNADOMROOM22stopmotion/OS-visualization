import tensorflow as tf
from tensorflow.keras import layers, models

# Number of features per process
FEATURES = 3   # arrival, burst, priority

# Number of output classes (algorithms)
NUM_CLASSES = 5

def build_model():
    inputs = tf.keras.Input(shape=(None, FEATURES))  
    # None = variable number of processes

    # Mask padded values (assuming padding = 0)
    x = layers.Masking(mask_value=0.0)(inputs)

    # LSTM to process sequence of processes
    x = layers.LSTM(64, return_sequences=False)(x)

    # Dense layers for decision making
    x = layers.Dense(64, activation='relu')(x)
    x = layers.Dropout(0.3)(x)

    outputs = layers.Dense(NUM_CLASSES, activation='softmax')(x)

    model = models.Model(inputs, outputs)

    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

if "__name__" == "main":
    model = build_model()
    model.summary()