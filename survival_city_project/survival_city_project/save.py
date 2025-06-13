import json
import os
from datetime import datetime

class SaveGameManager:
    def __init__(self, save_directory="saves"):
        self.save_directory = save_directory
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

    def save_game(self, game_state, save_name=None):
        save_name = save_name or f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_path = os.path.join(self.save_directory, save_name)
        try:
            with open(save_path, 'w') as f:
                json.dump(game_state, f, indent=4)
            return True, f"Game saved as {save_name}"
        except Exception as e:
            return False, f"Failed to save game: {str(e)}"

    def load_game(self, save_file):
        save_path = os.path.join(self.save_directory, save_file)
        if not os.path.exists(save_path):
            return False, "Save file not found"
        
        try:
            with open(save_path, 'r') as f:
                data = json.load(f)
                return True, data
        except Exception as e:
            return False, f"Failed to load game: {str(e)}"

    def list_saves(self):
        if not os.path.exists(self.save_directory):
            return []
        return [f for f in os.listdir(self.save_directory) 
               if f.endswith('.json') and os.path.isfile(os.path.join(self.save_directory, f))]

    def delete_save(self, save_file):
        save_path = os.path.join(self.save_directory, save_file)
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
                return True, f"Deleted save: {save_file}"
            except Exception as e:
                return False, f"Failed to delete save: {str(e)}"
        return False, "Save file not found"