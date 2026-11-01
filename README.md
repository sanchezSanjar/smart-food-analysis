# Smart Food Analysis

Recognise a meal from a photo and see an easy-to-read nutrition estimate.

## Run locally

Python 3.11+ is recommended.

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install torch
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

## Model

Food recognition uses [`nateraw/food`](https://huggingface.co/nateraw/food) (Apache-2.0), a Vision
Transformer fine-tuned on the Food-101 dataset (101 dishes).

## Limitations

The classifier predicts a likely dish; it does not detect every ingredient or measure portion size.
Nutrition values are estimates, not medical or dietary advice.

## License

MIT for the project code. Third-party models and dependencies keep their own licenses.
