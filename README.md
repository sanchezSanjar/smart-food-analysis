# Smart Food Analysis

A Streamlit prototype that classifies a meal photo and displays an easy-to-read, illustrative nutrition estimate.

## Features

- Upload JPG, JPEG, PNG, or WebP meal photos
- Pretrained image classification using Hugging Face Transformers
- Adjustable serving-size estimate
- Readable nutrition summary for calories, protein, carbohydrates, and fat
- Simple responsive Streamlit interface

## Important limitations

This is a learning/demo project, not a clinically validated nutrition system. The classifier predicts a likely food category; it does not detect every ingredient, estimate serving weight from the image, or guarantee correct results. Nutrition figures in `food_analyzer.py` are illustrative sample values, not a verified nutrition database. Replace them with a reliable, licensed nutrition API or database before using this for real dietary decisions.

## Run locally

Python 3.10 or 3.11 is recommended.

```bash
python -m venv .venv
```

Activate the environment:

- Windows PowerShell: `.venv\\Scripts\\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Install dependencies and launch:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

The first analysis may take time because the pretrained model is downloaded and cached. An internet connection is required on first run.

## Push to GitHub

1. Create a new empty repository on GitHub, for example `smart-food-analysis`.
2. Extract this project folder.
3. In a terminal opened inside the folder, run:

```bash
git init
git add .
git commit -m "Add smart food analysis prototype"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/smart-food-analysis.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username.

## Project structure

```text
smart-food-analysis-ai/
├── app.py
├── food_analyzer.py
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

## Model

The prototype uses [`nateraw/food`](https://huggingface.co/nateraw/food) through the Transformers image-classification pipeline. Review the model card and its license before distributing or deploying the project.

## License

This repository includes an MIT license for the project code. Third-party model weights and dependencies remain subject to their own licenses and terms.
