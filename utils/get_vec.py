import os

from transformers import AutoTokenizer, AutoModel
import torch
from dotenv import load_dotenv


load_dotenv()  # loads environment variables from .env file

model = AutoModel.from_pretrained("cl-tohoku/bert-base-japanese")
tokenizer = AutoTokenizer.from_pretrained("cl-tohoku/bert-base-japanese")


def text_to_vector(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].squeeze().numpy()

if __name__ == "__main__":


    text = "LINE株式会社で自然言語処理の研究・開発をしている。"
    vector = text_to_vector(text)
    print(vector)
    print(vector.shape)  # (768,)