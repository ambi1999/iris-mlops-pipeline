"""
test_app.py — Step 3 of the pipeline: automated TESTS.

Run them with:  pytest -v

pytest automatically finds files named test_*.py and runs every function
whose name starts with test_. Each `assert` is a check: if it is False,
the test fails, and in CI that stops the pipeline.

Note: run `python train.py` first, because the app needs model.joblib.
"""
from fastapi.testclient import TestClient  # calls the API without starting a server

from app import app  # the FastAPI application we want to test

# A fake "browser" that sends requests straight to our app in memory.
client = TestClient(app)


def test_health():
    """The health endpoint should answer with status 200 (OK)."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_setosa():
    """A flower with small petals is a classic setosa; the model must get it right."""
    flower = {"sepal_length": 5.1, "sepal_width": 3.5,
              "petal_length": 1.4, "petal_width": 0.2}
    response = client.post("/predict", json=flower)
    assert response.status_code == 200
    assert response.json()["species"] == "setosa"


def test_bad_input_rejected():
    """Sending text instead of numbers must be rejected with status 422
    (Unprocessable Entity), not crash the server."""
    response = client.post("/predict", json={"sepal_length": "oops"})
    assert response.status_code == 422
