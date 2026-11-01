"""One-time download of the food recognition model into models/food (needs internet)."""
from pathlib import Path

from huggingface_hub import snapshot_download

REPO_ID = "nateraw/food"
TARGET = Path(__file__).resolve().parent.parent / "models" / "food"


def main():
    TARGET.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {REPO_ID} into {TARGET} ...")
    snapshot_download(repo_id=REPO_ID, local_dir=str(TARGET),
                      allow_patterns=["config.json", "preprocessor_config.json",
                                      "*.safetensors", "pytorch_model.bin"])
    print("Done. Smart Food Analysis now works offline.")


if __name__ == "__main__":
    main()
