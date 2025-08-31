from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import numpy as np
from PIL import Image, UnidentifiedImageError
import io
from sklearn.metrics.pairwise import cosine_similarity
import tensorflow as tf
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input # type: ignore
from tensorflow.keras.preprocessing import image # type: ignore

# -------- Setup --------
app = FastAPI(title="Image Similarity API")

# ✅ Allow frontend (http://127.0.0.1:5500 etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dataset directory
DATASET_DIR = os.path.join(os.getcwd(), "dataset")

# Mount dataset folder (to serve images via /dataset/*)
if os.path.exists(DATASET_DIR):
    app.mount("/dataset", StaticFiles(directory=DATASET_DIR), name="dataset")

# Load pre-trained ResNet50 (without top classifier)
model = ResNet50(weights="imagenet", include_top=False, pooling="avg")

# -------- Helper Functions --------
def preprocess_image(img: Image.Image):
    """Resize & preprocess image for ResNet50"""
    img = img.resize((224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return preprocess_input(img_array)

def extract_features(img: Image.Image):
    """Extract ResNet50 features"""
    img_tensor = tf.constant(preprocess_image(img), dtype=tf.float32)
    features = model.predict(img_tensor, verbose=0)
    return features.flatten()

# -------- Precompute dataset features (recursive subfolders) --------
dataset_features = {}
if os.path.exists(DATASET_DIR):
    for root, _, files in os.walk(DATASET_DIR):  # ✅ includes subfolders
        for fname in files:
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, DATASET_DIR)  # e.g. "fruits/apple1.jpg"
            try:
                img = Image.open(fpath).convert("RGB")
                dataset_features[rel_path] = extract_features(img)
                print(f"Indexed: {rel_path}")
            except UnidentifiedImageError:
                print(f"Skipping (not image): {rel_path}")
            except Exception as e:
                print(f"Error loading {rel_path}: {e}")

print(f"✅ Dataset indexed: {len(dataset_features)} images")

# -------- API Endpoint --------
@app.post("/compare-image/")
async def compare_image(file: UploadFile = File(...)):
    try:
        # Read uploaded file
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")

        # Extract features of uploaded image
        uploaded_features = extract_features(img).reshape(1, -1)

        if not dataset_features:
            return JSONResponse({"error": "Dataset is empty!"}, status_code=400)

        # Compare with dataset features
        similarities = {}
        for rel_path, feat in dataset_features.items():
            score = cosine_similarity(uploaded_features, feat.reshape(1, -1))[0][0]
            similarities[rel_path] = float(score)

        # Sort results (highest similarity first)
        sorted_results = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

        return {
            "uploaded_file": file.filename,
            "most_similar": [
                {"path": rel_path, "score": score}
                for rel_path, score in sorted_results[:5]  # top 5 matches
            ]
        }

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
