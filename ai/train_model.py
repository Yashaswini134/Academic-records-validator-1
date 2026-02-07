"""
AI-based Certificate Forgery Detection - Training Module
This module trains a CNN model to detect forged certificates.
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
import cv2

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 20
MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), 'model', 'certificate_forgery_model.h5')

def load_dataset():
    """
    Load images from dataset/genuine and dataset/fake folders.
    Returns: X (images), y (labels)
    """
    genuine_path = os.path.join(os.path.dirname(__file__), 'dataset', 'genuine')
    fake_path = os.path.join(os.path.dirname(__file__), 'dataset', 'fake')
    
    images = []
    labels = []
    
    # Load genuine certificates (label = 0)
    if os.path.exists(genuine_path):
        for filename in os.listdir(genuine_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                img_path = os.path.join(genuine_path, filename)
                img = cv2.imread(img_path)
                if img is not None:
                    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    images.append(img)
                    labels.append(0)  # Genuine
    
    # Load fake certificates (label = 1)
    if os.path.exists(fake_path):
        for filename in os.listdir(fake_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                img_path = os.path.join(fake_path, filename)
                img = cv2.imread(img_path)
                if img is not None:
                    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    images.append(img)
                    labels.append(1)  # Fake
    
    if len(images) == 0:
        raise ValueError("No images found in dataset folders. Please add images to ai/dataset/genuine and ai/dataset/fake")
    
    # Convert to numpy arrays
    X = np.array(images, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)
    
    # Normalize pixel values to [0, 1]
    X = X / 255.0
    
    print(f"Loaded {len(images)} images:")
    print(f"  - Genuine: {np.sum(y == 0)}")
    print(f"  - Fake: {np.sum(y == 1)}")
    
    return X, y

def create_cnn_model():
    """
    Create a CNN model for binary classification (genuine vs fake).
    """
    model = keras.Sequential([
        # Input layer
        layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3)),
        
        # Convolutional Block 1
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Convolutional Block 2
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Convolutional Block 3
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Convolutional Block 4
        layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Flatten and Dense layers
        layers.Flatten(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        
        # Output layer (sigmoid for binary classification)
        layers.Dense(1, activation='sigmoid')
    ])
    
    return model

def train_model():
    """
    Main training function.
    """
    print("=" * 60)
    print("AI-based Certificate Forgery Detection - Training")
    print("=" * 60)
    
    # Load dataset
    print("\n[1/5] Loading dataset...")
    X, y = load_dataset()
    
    # Split into train and validation sets
    print("\n[2/5] Splitting dataset...")
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    
    # Create data augmentation for training
    train_datagen = ImageDataGenerator(
        rotation_range=10,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.1,
        horizontal_flip=False,
        fill_mode='nearest'
    )
    
    # Create model
    print("\n[3/5] Creating CNN model...")
    model = create_cnn_model()
    
    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    
    print("\nModel Summary:")
    model.summary()
    
    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7
        )
    ]
    
    # Train model
    print(f"\n[4/5] Training model for {EPOCHS} epochs...")
    history = model.fit(
        train_datagen.flow(X_train, y_train, batch_size=BATCH_SIZE),
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate model
    print("\n[5/5] Evaluating model...")
    val_loss, val_accuracy, val_precision, val_recall = model.evaluate(X_val, y_val, verbose=0)
    print(f"\nValidation Results:")
    print(f"  - Loss: {val_loss:.4f}")
    print(f"  - Accuracy: {val_accuracy:.4f}")
    print(f"  - Precision: {val_precision:.4f}")
    print(f"  - Recall: {val_recall:.4f}")
    
    # Save model
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    model.save(MODEL_SAVE_PATH)
    print(f"\n✓ Model saved to: {MODEL_SAVE_PATH}")
    print("=" * 60)
    print("Training completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    # Set random seeds for reproducibility
    np.random.seed(42)
    tf.random.set_seed(42)
    
    # Run training
    train_model()
