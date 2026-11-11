"""
app.py — Step 2 of the pipeline: SERVE the model as a web API.

Run it with:  uvicorn app:app --reload
Then open:    http://localhost:8000/docs   (interactive API page)

Endpoints:
  GET  /health   -> {"status": "ok"}  used by monitoring tools to check
                    the service is alive
  POST /predict  -> send flower measurements, get back a species name
"""
import joblib                   # loads the model file created by train.py
from fastapi import FastAPI     # the web framework
from pydantic import BaseModel  # describes and validates the input data

# The model predicts a number (0, 1 or 2); this list turns it into a name.
SPECIES = ["setosa", "versicolor", "virginica"]

# Create the web application. The title appears on the /docs page.
app = FastAPI(title="Iris classifier")

# Load the trained model ONCE when the app starts, not on every request,
# so predictions are fast.
model = joblib.load("model.joblib")


class Flower(BaseModel):
    """The input the API expects. FastAPI automatically rejects requests
    that are missing a field or send text instead of a number (HTTP 422)."""
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


@app.get("/health")
def health():
    """Health check: if this answers, the service is up and running."""
    return {"status": "ok"}


@app.post("/predict")
def predict(flower: Flower):
    """Take one flower's measurements and return the predicted species."""
    # scikit-learn expects a list of rows, so we wrap our one flower in [[...]]
    features = [[flower.sepal_length, flower.sepal_width,
                 flower.petal_length, flower.petal_width]]
    prediction = int(model.predict(features)[0])  # e.g. 0
    return {"species": SPECIES[prediction]}       # e.g. "setosa"
