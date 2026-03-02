import random

# Replace the old scrolling function with the fixed randrange

def scroll():
    scroll_distance = random.randrange(300, 500)
    # scrolling logic

# Replace Unicode emojis with plain text

def print_status(status):
    if status == "⏳":
        print("Waiting")
    elif status == "✅":
        print("Success")
    elif status == "❌":
        print("Error")
    else:
        print(status)

# Keep rest of your logic including:
# 1. OCR text extraction
# 2. Account_Outputs folder handling
# 3. Human-like mouse movements
# 4. Operating hours checking
