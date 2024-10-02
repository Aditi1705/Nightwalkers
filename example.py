from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import warnings
import random
import json

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
        scenarios = json.load(f)
    return scenarios

# Initialize user history
user_history = {}

def chat(user_id, user_message):
    # Initialize user history if not already done
    if user_id not in user_history:
        user_history[user_id] = {
            "current_scenario": None,
            "choices": [],
            "consequence": None
        }

    # Load scenarios from dataset
    scenarios = load_and_tokenize_dataset()

    # If no scenario has been presented yet (first interaction)
    if user_history[user_id]["current_scenario"] is None:
        # Randomly select a scenario for the first response
        scenario = random.choice(scenarios)
        scenario_text = scenario["scenario"]
        choices = scenario["choices"]

        # Update user history with the current scenario
        user_history[user_id]["current_scenario"] = scenario_text
        user_history[user_id]["choices"] = choices

        choices_str = ', '.join(user_history[user_id]["choices"])
        
        # Return the scenario and choices to the user (no consequence yet)
        return f"{scenario_text} You can {choices_str}. What choice will you make?"

    else:
        # Process the user's choice
        user_choice = user_message.strip()
        user_history[user_id]["choices"].append(user_choice)

        # Prepare input for the model
        scenario_text = user_history[user_id]["current_scenario"]
        input_text = f"What is the consequence of {user_choice} when {scenario_text}?"
        input_ids = tokenizer.encode(input_text + tokenizer.eos_token, return_tensors="pt")

        # Generate a response
        with torch.no_grad():
            chat_history_ids = model.generate(
                input_ids,
                max_length=500,
                pad_token_id=tokenizer.eos_token_id,
            )
        bot_message = tokenizer.decode(chat_history_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)

        # Generate a new random scenario and choices for the next interaction
        scenario = random.choice(scenarios)
        scenario_text = scenario["scenario"]
        choices = scenario["choices"]

        # Update user history with the current scenario
        user_history[user_id]["current_scenario"] = scenario_text
        user_history[user_id]["choices"] = choices
        
        choices_str = ', '.join(user_history[user_id]["choices"])

        # Return the bot's message, consequence of the user's choice, next scenario, and next choices
        return f"{bot_message} {scenario_text} You can {choices_str}. What choice will you make?"

# Run the chat function for testing
if __name__ == "__main__":
    user_id = "user1"
    
    # Simulating first interaction
    print(chat(user_id, ""))
    
    while True:
        # Simulating user choice
        user_choice = input("Enter your choice: ")
        response = chat(user_id, user_choice)
        print(response)
        
