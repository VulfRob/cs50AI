import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    evidence = []
    labels = []

    # Месяцы
    months = {
        "Jan": 0, "January": 0,
        "Feb": 1, "February": 1,
        "Mar": 2, "March": 2,
        "Apr": 3, "April": 3,
        "May": 4,
        "Jun": 5, "June": 5,
        "Jul": 6, "July": 6,
        "Aug": 7, "August": 7,
        "Sep": 8, "September": 8,
        "Oct": 9, "October": 9,
        "Nov": 10, "November": 10,
        "Dec": 11, "December": 11
    }

    # Индексы признаков по типам
    int_cols   = [0, 2, 4, 11, 12, 13, 14]   # все, которые int (без Month, VisitorType, Weekend)
    float_cols = [1, 3, 5, 6, 7, 8, 9]       # все float

    with open(filename, "r") as f:
        reader = csv.reader(f)
        next(reader)  # пропустить заголовок

        for row in reader:
            X = row[0:17]
            Y = row[17]

            # int
            for i in int_cols:
                X[i] = int(X[i])

            # float
            for i in float_cols:
                X[i] = float(X[i])

            # Month → число
            X[10] = months[X[10]]

            # VisitorType
            X[15] = 1 if X[15] == "Returning_Visitor" else 0

            # Weekend
            X[16] = 1 if X[16] == "TRUE" else 0

            # Label
            Y = 1 if Y == "TRUE" else 0

            evidence.append(X)
            labels.append(Y)

    return evidence, labels


def train_model(evidence, labels):
    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    TP = 0  # true positives
    TN = 0  # true negatives
    P = 0  # all actual positives
    N = 0  # all actual negatives

    for true, pred in zip(labels, predictions):
        if true == 1:
            P += 1
            if pred == 1:
                TP += 1
        else:  # true == 0
            N += 1
            if pred == 0:
                TN += 1

    sensitivity = TP / P
    specificity = TN / N

    return sensitivity, specificity


if __name__ == "__main__":
    main()
