import os
import random
import json
from flask import Flask, jsonify, request, send_from_directory
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import warnings

# Initialize Flask app
app = Flask(__name__)

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*right-padding was detected.*")

# Load GPT-2 Model and Tokenizer from Hugging Face
model_name = "microsoft/DialoGPT-medium"  # You can also use "gpt2-medium", "gpt2-large", or "gpt2-xl"
tokenizer = GPT2Tokenizer.from_pretrained(model_name, padding_side='left')
model = GPT2LMHeadModel.from_pretrained(model_name)

# Load RPG game dataset
def load_and_tokenize_dataset():
    with open("dataset.json") as f:
        return json.load(f)

# Store user history and choices
user_history = {}

# Serve home page
@app.route('/')
def home():
    return send_from_directory('Frontend', 'home.html')

# Serve main adventure page
@app.route('/main')
def main():
    return send_from_directory('Frontend', 'main.html')

# Serve static files like CSS, JS, images, etc.
@app.route('/Frontend/<path:filename>')
def serve_static_files(filename):
    return send_from_directory('Frontend', filename)

# Chat endpoint for processing messages
@app.route('/chat', methods=['POST'])
def chat():
    user_id = request.json.get('user_id')  # Unique ID for user sessions
    user_message = request.json.get('message')

    # Initialize user history if not already done
    if user_id not in user_history:
        user_history[user_id] = {
            "current_scenario": None,
            "choices": [],
            "consequence": None
        }

    # Load scenarios from dataset
    scenarios = load_and_tokenize_dataset()

    # Process the user's choice for subsequent interactions
    user_choice = user_message.strip()
    user_history[user_id]["choices"].append(user_choice)

    # Prepare input for the model (optional: include GPT-2 for generating more dynamic responses)
    scenario_text = user_history[user_id]["current_scenario"]  # Fetch the current scenario
    input_text = f"What is the consequence of {user_choice} when {scenario_text}?"
    input_ids = tokenizer.encode(input_text + tokenizer.eos_token, return_tensors="pt")

    # Generate a response (GPT-2 response generation)
    with torch.no_grad():
        chat_history_ids = model.generate(
            input_ids,
            max_length=1000,
            pad_token_id=tokenizer.eos_token_id,
        )
    bot_message = tokenizer.decode(chat_history_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)

    # Generate a new random scenario and choices for the next interaction
    scenario = random.choice(scenarios)
    next_scenario_text = scenario["scenario"]
    next_choices = scenario["choices"]

    # Update user history with the new scenario and choices
    user_history[user_id]["current_scenario"] = next_scenario_text
    user_history[user_id]["choices"] = next_choices

    next_choices_str = ', '.join(next_choices)

    # Return the bot's message (consequence), next scenario, and next choices
    return jsonify({
        'response': f"{bot_message} {next_scenario_text} You can {next_choices_str}. What choice will you make?"
    })

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)





