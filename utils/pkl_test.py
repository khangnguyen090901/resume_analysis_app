import pickle
import os

# Luôn load từ thư mục gốc của project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
label_path = os.path.join(BASE_DIR, "model", "label_encoder.pkl")

with open(label_path, "rb") as f:
    le = pickle.load(f)

print(le.classes_)

