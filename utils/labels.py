import pickle
import os

def load_label_encoder():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    label_path = os.path.join(base_dir, "model", "label_encoder.pkl")
    with open(label_path, "rb") as f:
        return pickle.load(f)
