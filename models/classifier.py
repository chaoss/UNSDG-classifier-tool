import torch
from torch import nn
from transformers import AutoTokenizer, AutoModel
from huggingface_hub import hf_hub_download
from pathlib import Path
print(torch.version.cuda)        # should show 12.8
print(torch.cuda.is_available())

# --- 1. Define the Model Architecture ---
# This class must match the architecture used during training.
# You can copy this class from the original training script.
class SDGClassifier(nn.Module):
    def __init__(self, model_path, pooler_dropout, class_number):
        super().__init__()
        self.bert = AutoModel.from_pretrained(model_path)
        
        # Checkpoint stores custom pooler AS bert.pooler (overwrites LUKE's built-in)
        # so assign it directly onto self.bert.pooler, not as self.pooler
        self.bert.pooler = nn.Sequential(
            nn.Linear(self.bert.config.hidden_size, self.bert.config.hidden_size)
        )
        
        self.dropout = nn.Dropout(pooler_dropout)
        self.tanh = nn.Tanh()
        
        # cls.0.* → Sequential
        self.cls = nn.Sequential(
            nn.Linear(self.bert.config.hidden_size, class_number)
        )

    def forward(self, input_ids, attention_mask, token_type_ids, position, labels=None):
        out = self.bert(
            input_ids,
            attention_mask,
            token_type_ids=token_type_ids,
            output_attentions=True,
            output_hidden_states=True,
        )
        hidden = out.last_hidden_state
        mask   = attention_mask.unsqueeze(-1).float()
        avg    = (hidden * mask).sum(1) / mask.sum(1)

        pooled = self.tanh(self.bert.pooler(self.dropout(avg)))
        logits = self.cls(pooled)
        return logits, avg, out.attentions

# --- 2. Setup and Load Model ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
# Model configuration
BASE_MODEL = 'studio-ousia/luke-large-lite'
NUM_CLASSES = 17
DROPOUT_RATE = 0.26 # This is the optimized dropout rate from the paper's training

# Instantiate the model
model = SDGClassifier(model_path=BASE_MODEL, pooler_dropout=DROPOUT_RATE, class_number=NUM_CLASSES).to(device)
model.eval() # Set to evaluation mode

# Download the fine-tuned weights from this Hub
model_weights_path = hf_hub_download(
    repo_id="GE-Lab/SDGs-classifier",
    filename="best_model.pt"
)

# # Load the weights into the model
# model.load_state_dict(torch.load(model_weights_path, map_location=device))
state_dict   = torch.load(model_weights_path, map_location=device)
model.load_state_dict(state_dict, strict=True)

print("Model loaded successfully!")
