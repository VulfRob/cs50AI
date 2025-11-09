import cv2
import numpy as np
import os
import sys
import tensorflow as tf



from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.layers import BatchNormalization


EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    images = []
    labels = []

    # перебор всех подпапок внутри data_dir
    for label in os.listdir(data_dir):
        folder_path = os.path.join(data_dir, label)

        # проверяем, что это папка
        if not os.path.isdir(folder_path):
            continue

        # проходим по всем файлам в папке
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # читаем изображение
            img = cv2.imread(file_path)
            if img is None:
                continue  # если файл не удалось открыть

            # меняем размер
            img_resized = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))

            images.append(img_resized)
            labels.append(int(label))  # имя папки — категория

    return images, labels



def get_model():
    model = Sequential([
        # Блок 1
        Conv2D(32, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)),
        BatchNormalization(),
        Conv2D(32, (3, 3), activation="relu"),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),

        # Блок 2
        Conv2D(64, (3, 3), activation="relu"),
        BatchNormalization(),
        Conv2D(64, (3, 3), activation="relu"),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),

        # превращаем 2D в 1D
        Flatten(),

        # полносвязный слой
        Dense(128, activation="relu"),
        Dropout(0.5),

        # выходной слой
        Dense(NUM_CATEGORIES, activation="softmax")
    ])

    # компиляция модели
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model



if __name__ == "__main__":
    main()
