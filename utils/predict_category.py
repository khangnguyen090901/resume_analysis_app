from transformers import BertTokenizer, BertForSequenceClassification
import torch
from utils.labels import load_label_encoder
import os

# Load model & tokenizer
model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")
tokenizer = BertTokenizer.from_pretrained(model_dir)
model = BertForSequenceClassification.from_pretrained(model_dir)
model.eval()

# Load label encoder
label_encoder = load_label_encoder()
id2label = dict(enumerate(label_encoder.classes_))

def predict_category(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        pred = torch.argmax(outputs.logits, dim=1).item()
    return id2label[pred]
