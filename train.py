"""
train.py — Step 1 of the pipeline: TRAIN, EVALUATE and SAVE a model.

Run it with:  python train.py

What it does:
  1. Loads the Iris flower dataset (150 flowers, 3 species).
  2. Splits it into training data and test data.
  3. Trains a simple classifier.
  4. Measures accuracy on the test data the model has never seen.
  5. Saves the model (model.joblib) and its score (metrics.json).
  6. Exits with an error if accuracy is too low (the "quality gate"),
     which makes the CI pipeline fail so a bad model never ships.
"""
import json  # writes the metrics file in a format other tools can read
import sys   # lets us exit with an error code to fail the pipeline

import joblib                                         # saves/loads the model file
from sklearn.datasets import load_iris                # built-in example dataset
from sklearn.linear_model import LogisticRegression   # the model we train
from sklearn.metrics import accuracy_score            # % of correct predictions
from sklearn.model_selection import train_test_split  # splits data in two

# Quality gate: the minimum accuracy a model must reach to be accepted.
MIN_ACCURACY = 0.85

# Fixing the random seed makes the split identical every run, so results
# are reproducible on any machine (your laptop, CI, Docker).
RANDOM_SEED = 42

# X = flower measurements (inputs), y = species labels (answers)
X, y = load_iris(return_X_y=True)

# Keep 20% of the data aside for testing. The model never sees it during
# training, so the test score tells us how it handles new data.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_SEED
)

# Create and train the model. max_iter gives the training algorithm
# enough steps to finish learning.
model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)

# Evaluate on the unseen test data.
accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"Test accuracy: {accuracy:.3f}")

# Save the trained model as a file (the "model artifact").
joblib.dump(model, "model.joblib")

# Save the score so people and tools can track it over time.
with open("metrics.json", "w") as f:
    json.dump({"accuracy": accuracy}, f, indent=2)

# The quality gate. sys.exit(1) signals failure to whatever ran this
# script; in GitHub Actions that turns the pipeline red and stops it.
if accuracy < MIN_ACCURACY:
    print(f"FAIL: accuracy below {MIN_ACCURACY}")
    sys.exit(1)

print("Model saved to model.joblib")
