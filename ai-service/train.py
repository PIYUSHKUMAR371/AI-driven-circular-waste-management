import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
import os

# ==============================
# DATASET PATH
# ==============================
data_dir = "archive/1024+/entrainement"

img_size = (224, 224)
batch_size = 32

# ==============================
# LOAD DATASET
# ==============================
train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=img_size,
    batch_size=batch_size
)

print("TRAINING CLASS ORDER:", train_ds.class_names)

val_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=img_size,
    batch_size=batch_size
)

class_names = train_ds.class_names
print("Classes:", class_names)

# ==============================
# OPTIMIZE DATA PIPELINE
# ==============================
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# ==============================
# COMPUTE CLASS WEIGHTS
# ==============================
y_train = np.concatenate([y for x, y in train_ds], axis=0)

class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y_train),
    y=y_train
)

class_weights = dict(enumerate(class_weights))
print("Class Weights:", class_weights)

# ==============================
# DATA AUGMENTATION
# ==============================
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
])

# ==============================
# LOAD PRETRAINED MODEL
# ==============================
base_model = MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet"
)

base_model.trainable = False  # Freeze base model initially

# ==============================
# BUILD MODEL
# ==============================
model = models.Sequential([
    data_augmentation,
    layers.Rescaling(1./255),
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.4),
    layers.Dense(len(class_names), activation='softmax')
])

# ==============================
# COMPILE
# ==============================
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# ==============================
# TRAIN (PHASE 1)
# ==============================
print("\n--- Training Phase 1 (Frozen Base Model) ---\n")

model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=15,
    class_weight=class_weights
)

# ==============================
# FINE-TUNING (PHASE 2)
# ==============================
print("\n--- Fine-Tuning Last Layers ---\n")

base_model.trainable = True

# Freeze early layers, unfreeze last 20
for layer in base_model.layers[:-20]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=5,
    class_weight=class_weights
)

# ==============================
# SAVE MODEL
# ==============================
model.save("waste_classifier_model_v3.keras")

print("\nModel saved as waste_classifier_model_v3.keras")