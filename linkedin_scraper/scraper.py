import pyautogui
import time
import random

def manual_login_instructions():
    print("Please log into your LinkedIn account manually before starting the scraping.")
    print("You have 10 seconds to switch to the LinkedIn window.")
    time.sleep(10)

def human_like_mouse_move(x, y):
    # Move mouse in a human-like manner
    current_x, current_y = pyautogui.position()
    steps = random.randint(10, 20)  # Number of steps
    for i in range(steps):
        intermediate_x = current_x + (x - current_x) * (i / steps) + random.randint(-5, 5)
        intermediate_y = current_y + (y - current_y) * (i / steps) + random.randint(-5, 5)
        pyautogui.moveTo(intermediate_x, intermediate_y, duration=random.uniform(0.1, 0.3))
    pyautogui.click()

def main():
    manual_login_instructions()
    
    # Example usage of human_like_mouse_move
    profiles = [(x1, y1), (x2, y2)]  # Replace with actual profile coordinates
    for profile in profiles:
        current_time = time.localtime()
        if (current_time.tm_wday < 5 and 
            (9 <= current_time.tm_hour < 17 or (current_time.tm_hour == 17 and current_time.tm_min < 30))):
            human_like_mouse_move(profile[0], profile[1])
            time.sleep(random.randint(60, 600))  # Delay between actions

if __name__ == "__main__":
    main()
