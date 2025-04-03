import re
from transformers import pipeline
import difflib


# Load a Hugging Face model pipeline (text generation for suggestions)
suggestion_model = pipeline("text2text-generation", model="google/flan-t5-small")

# List of predefined commands
commands = [
    re.compile("make me (a|an) (.*) appointment from (.*) to (.*) from \d{2}:\d{2} to \d{2}:\d{2} at (.*)", re.IGNORECASE),
    re.compile("show my (one time|reccuring) appointments", re.IGNORECASE),
    re.compile("show my appointments for (today|tomorrow|(.*))", re.IGNORECASE),
    re.compile("show home page", re.IGNORECASE),
    re.compile("show my (.*) schedule", re.IGNORECASE),
    re.compile("show my schedule for (Monday|Tuesday|Wednesday|Thrusday|Friday|Saturday|Sunday|work)", re.IGNORECASE),
    "show weather",
    re.compile("remove my (.*) appointment from (.*) to (.*) at \d{2}:\d{2}", re.IGNORECASE),
    re.compile("remove my (.*) appointment for (.*) at \d{2}:\d{2}", re.IGNORECASE),
    re.compile("make me (a|an) (.*) appointment for (.*) from \d{2}:\d{2} to \d{2}:\d{2} at (.*)", re.IGNORECASE),
    re.compile("schedule me for (Monday|Tuesday|Wednesday|Thrusday|Friday|Saturday|Sunday|work) (.*) from \d{2}:\d{2} to \d{2}:\d{2} at (.*)", re.IGNORECASE),
    re.compile("remove from my (Monday|Tuesday|Wednesday|Thrusday|Friday|Saturday|Sunday|work) schedule (.*) at \d{2}:\d{2}", re.IGNORECASE),
    "show home page"
]

# Preprocess commands: convert regex patterns to strings
commands_as_strings = [
    cmd.pattern if isinstance(cmd, re.Pattern) else cmd for cmd in commands
]

def suggest_with_model(user_input):
    """Get command suggestion using Hugging Face model."""
    prompt = f"The user entered the command '{user_input}'. Suggest the correct command from this list: {commands_as_strings}."
    try:
        response = suggestion_model(prompt, max_length=50, num_return_sequences=1)
        return response[0]['generated_text'].strip()
    except Exception as e:
        print("Error using Hugging Face model:", e)
        return None

def suggest_command(user_input):
    """Suggest a similar command."""
    # Find closest match using difflib
    suggestions = difflib.get_close_matches(user_input, commands_as_strings, n=1, cutoff=0.6)
    if suggestions:
        return f"Did you mean '{suggestions[0]}'?"
    else:
        model_suggestion = suggest_with_model(user_input)
        if model_suggestion:
            return f"Did you mean '{model_suggestion}'?"
        else:
            return "No suggestions available."

