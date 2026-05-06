import tkinter as tk
from src.ui import PetMedApp
import json

DATA_FILE = "pets_data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"pets": [], "schedules": [], "intakes": []}

def save_data(d): # used to save the data back to the json file after any changes are made to it in the app
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    PetMedApp(root, save_data, load_data)
    root.mainloop()