# Getting Started: Step-by-Step Guide

This guide walks you through running the whole project on your own computer, one command at a time. Every command comes with an explanation of what it does and what you should see, so you can follow along even if uv, Git or Docker are new to you.

Commands are shown for **Windows** (Command Prompt or the VS Code terminal). Where macOS or Linux differ, it's noted.

**Contents**

1. [Install the tools](#1-install-the-tools)
2. [Get your own copy of the project](#2-get-your-own-copy-of-the-project)
3. [Set up the Python environment](#3-set-up-the-python-environment)
4. [Train the model](#4-train-the-model)
5. [Run the tests](#5-run-the-tests)
6. [Start the prediction API](#6-start-the-prediction-api)
7. [Explore the notebooks](#7-explore-the-notebooks)
8. [Run the app in Docker](#8-run-the-app-in-docker)
9. [Watch the CI pipeline on GitHub](#9-watch-the-ci-pipeline-on-github)
10. [Everyday uv commands](#10-everyday-uv-commands)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Install the tools

| Tool | What it's for | Required? |
|------|---------------|-----------|
| [Git](https://git-scm.com) | Downloads the project and tracks changes | Yes |
| [uv](https://docs.astral.sh/uv/) | Installs Python and all packages | Yes |
| [VS Code](https://code.visualstudio.com) + the **Python** and **Jupyter** extensions | Editor for the code and notebooks | Recommended |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Runs the app in a container (section 8) | Optional |

You don't need to install Python yourself: uv does it for you in section 3.

**Install uv on Windows:**

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

This downloads and runs uv's official installer. `-ExecutionPolicy ByPass` allows the installer script to run just this once, without changing your system settings.

**Install uv on macOS or Linux:**

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Check it worked.** Close and reopen your terminal (so it notices the newly installed program), then run:

```
uv --version
```

You should see a version number such as `uv 0.11.x`.

---

## 2. Get your own copy of the project

1. On this repository's GitHub page, click **Fork** (top right). This creates your own copy under your GitHub account, so the CI pipeline will run for you too.
2. On **your** fork's page, click the green **Code** button and copy the HTTPS URL.
3. In a terminal, go to the folder where you keep projects, then run:

```
git clone <paste-the-url-here>
cd iris-mlops-pipeline
```

- `git clone` downloads the project, including its full history, into a new folder.
- `cd` ("change directory") moves your terminal into that folder. **Every command from here on must be run from inside this folder.**

To open the project in VS Code, use **File → Open Folder** and choose the `iris-mlops-pipeline` folder.

---

## 3. Set up the Python environment

```
uv sync
```

This one command reads three files and builds everything you need:

- **`.python-version`** says which Python to use (3.13). If you don't have it, uv downloads it. It won't interfere with any other Python on your computer.
- **`pyproject.toml`** lists the packages the project needs.
- **`uv.lock`** records the *exact* version of every package, so you get precisely the same setup as everyone else, including the CI pipeline.

uv then creates a **`.venv`** folder (a "virtual environment": a private Python installation just for this project) and installs everything into it.

**Expected output:** a list of installed packages, ending with a line like `Installed 98 packages` (the exact number may differ).

**In VS Code:** press **Ctrl+Shift+P**, run **Python: Select Interpreter**, and choose the one marked **`.venv`**. This makes VS Code use the same environment as your terminal.

---

## 4. Train the model

### First, what does `uv run` do?

`uv run <command>` runs a command **inside the project's `.venv`**. That means it uses the project's Python 3.13 and the exact packages from `uv.lock`, not whatever else is installed on your computer. It also checks the environment is up to date first, so you never need to "activate" anything.

### Now train

```
uv run python train.py
```

- `uv run` uses the project environment (explained above).
- `python train.py` runs the training script.

The script loads the Iris flower dataset, trains a model, tests it on data it hasn't seen, and saves two files:

- **`model.joblib`**: the trained model (the "artifact")
- **`metrics.json`**: its accuracy score

**Expected output:**

```
Test accuracy: 1.000
Model saved to model.joblib
```

If accuracy were below 85%, the script would stop with an error instead. That's the **quality gate**, the same check that runs in the CI pipeline.

---

## 5. Run the tests

```
uv run pytest -v
```

- `pytest` finds every file named `test_*.py` and runs the test functions inside.
- `-v` ("verbose") lists each test by name with its result, instead of just dots.

The tests check that the API is alive, that it predicts a known flower correctly, and that it rejects bad input. They need `model.joblib`, so run section 4 first.

**Expected output** ends with:

```
3 passed
```

---

## 6. Start the prediction API

```
uv run uvicorn app:app --reload
```

- `uvicorn` is the web server that runs the app.
- `app:app` means "in the file `app.py`, use the object called `app`".
- `--reload` restarts the server automatically whenever you save a code change. It's handy while developing, but never used in production.

**Expected output** includes:

```
Uvicorn running on http://127.0.0.1:8000
```

**Try it:** open **http://127.0.0.1:8000/docs** in your browser. You'll get an interactive page listing the API's endpoints:

- **GET /health** answers `{"status": "ok"}` if the service is up.
- **POST /predict**: click it, then **Try it out**, edit the measurements, and click **Execute** to get a prediction.

**Stop the server** with **Ctrl+C** in the terminal.

---

## 7. Explore the notebooks

The `notebooks` folder has two guided walkthroughs, each about 15–20 minutes:

| Notebook | Covers |
|----------|--------|
| `01_mlops_demo.ipynb` | Data, training, quality gates, model artifacts, reproducibility, serving, drift monitoring |
| `02_devops_demo.ipynb` | Version control, locked versions, testing, Docker, CI, operations |

To run them in VS Code:

1. Open a notebook from the Explorer.
2. Click **Select Kernel** (top right) → **Python Environments** → **`.venv`**.
3. Run the cells in order with **Shift+Enter**.

No installation option: use the **Open in Colab** buttons in the README. Everything works there except the live Docker section, which shows sample output instead.

---

## 8. Run the app in Docker

*Optional. Requires Docker Desktop to be installed and running ("Engine running" in its window).*

### Build the image

```
docker build -t iris-mlops-pipeline .
```

- `docker build` follows the recipe in the `Dockerfile` to create an **image**: a frozen package containing Python, the packages, the code and a freshly trained model.
- `-t iris-mlops-pipeline` gives the image a name (a "tag") so you can refer to it later.
- `.` (the final dot) means "use the current folder as the build context". Don't leave it out.

The first build takes a minute or two. Later builds reuse cached steps and take seconds.

### Run a container

```
docker run --rm -p 8000:8000 iris-mlops-pipeline
```

- `docker run` starts a **container**, a running copy of the image.
- `--rm` deletes the container automatically when it stops, so old ones don't pile up.
- `-p 8000:8000` connects port 8000 on your computer to port 8000 inside the container (the format is `your-computer:container`). Without it, your browser couldn't reach the app.

Open **http://127.0.0.1:8000/docs** just as in section 6. This time the app runs entirely inside the container, using none of the Python on your computer.

**Stop it** with **Ctrl+C**.

---

## 9. Watch the CI pipeline on GitHub

Every time you push a change to your fork, GitHub Actions runs the pipeline in `.github/workflows/ci.yml` on a fresh machine: install → train → test → save the model → build the Docker image.

1. Open your fork on GitHub and click the **Actions** tab.
2. Click the latest run to watch each step. A green ✅ means everything passed.
3. The trained model is attached to the run under **Artifacts**.

### Try it: make the pipeline fail on purpose

In `train.py`, change:

```python
MIN_ACCURACY = 0.85
```

to:

```python
MIN_ACCURACY = 1.01
```

Then commit and push:

```
git commit -am "Test the quality gate"
git push
```

- `git commit` saves a snapshot of your changes. `-a` includes every file you've modified, and `-m` attaches a message describing the change.
- `git push` uploads your commits to GitHub, which starts the pipeline.

Watch the run turn red ❌ at the training step: no model can reach 101% accuracy, so the gate blocks it. Change the value back to `0.85`, commit and push again, and it turns green.

---

## 10. Everyday uv commands

| Command | What it does |
|---------|--------------|
| `uv sync` | Makes `.venv` match `uv.lock` exactly. Run it after pulling changes. |
| `uv run <command>` | Runs a command inside the project environment |
| `uv add <package>` | Adds a package the app needs, updating `pyproject.toml` and `uv.lock` |
| `uv add --dev <package>` | Adds a tool needed only for development (like pytest) |
| `uv remove <package>` | Removes a package |
| `uv lock --upgrade` | Upgrades all packages to their newest allowed versions |
| `uv python pin 3.14` | Changes the project's Python version in `.python-version` |

Whenever `pyproject.toml` or `uv.lock` changes, **commit both**. CI runs `uv sync --locked`, which fails on purpose if the lock file is out of date.

---

## 11. Troubleshooting

**"Python was not found; run without arguments to install from the Microsoft Store"**
Windows has a shortcut that redirects `python` to the Microsoft Store. You don't need it, because uv provides Python. Always use `uv run python ...` instead of plain `python`. To remove the shortcut, go to **Settings → Apps → Advanced app settings → App execution aliases** and turn off **python.exe** and **python3.exe**.

**"'uv' is not recognized as an internal or external command"**
The terminal was opened before uv was installed. Close and reopen the terminal, or restart VS Code entirely.

**"running scripts is disabled on this system" (PowerShell)**
Run this once, then open a new terminal:

```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**VS Code uses the wrong Python version**
Press **Ctrl+Shift+P** → **Python: Select Interpreter** and choose the **`.venv`** entry, not a global or Anaconda Python. Do the same for notebooks via **Select Kernel**.

**pytest error: "import file mismatch" or tests collected from unexpected folders**
pytest searches every subfolder for test files. Make sure there are no old copies of the project *inside* the project folder, then delete the caches and try again:

```
rmdir /s /q __pycache__
rmdir /s /q .pytest_cache
uv run pytest -v
```

(On macOS/Linux: `rm -rf __pycache__ .pytest_cache`.)

**Git warning: "LF will be replaced by CRLF" (or the reverse)**
Windows and Linux mark line endings differently. The project's `.gitattributes` file makes Git store everything with Linux-style LF endings, so this warning is harmless. To stop VS Code creating files with Windows endings, open **File → Preferences → Settings**, search for **eol**, and set **Files: Eol** to **\n**.

**CI fails at "Install Python and dependencies" with a lock file error**
`pyproject.toml` was changed but `uv.lock` wasn't updated or committed. Run `uv lock`, then commit and push `uv.lock`.

**Docker: "Cannot connect to the Docker daemon" or "error during connect"**
Docker Desktop isn't running. Start it and wait until it shows **Engine running**.

**"Address already in use" / port 8000 is busy**
Another server (often the one from section 6) is still running. Stop it with **Ctrl+C** in its terminal, or use a different port, for example `docker run --rm -p 8001:8000 iris-mlops-pipeline`, then open http://127.0.0.1:8001/docs.
