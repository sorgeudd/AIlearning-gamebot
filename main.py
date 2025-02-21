import tkinter as tk
from tkinter import ttk, messagebox
from game_environment import GameEnvironment
from ai_core import AIBot
import threading
import time

class GameAIInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Game AI Learning Interface")
        self.root.geometry("400x300")  # Set window size
        self.setup_ui()

        print("Initializing game environment...")
        self.game_env = GameEnvironment()
        print("Initializing AI bot...")
        self.ai_bot = AIBot()

        self.is_running = False
        self.is_learning = False

    def setup_ui(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Status label
        self.status_label = ttk.Label(main_frame, text="Status: Ready")
        self.status_label.pack(pady=10)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        # Control buttons
        self.learn_button = ttk.Button(button_frame, text="Learn from Gameplay", 
                                     command=self.toggle_learning)
        self.learn_button.pack(side=tk.LEFT, padx=5)

        self.start_button = ttk.Button(button_frame, text="Start AI Control", 
                                     command=self.start_ai)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                    command=self.stop_all)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Window region frame
        region_frame = ttk.LabelFrame(main_frame, text="Game Window Region", padding="5")
        region_frame.pack(fill=tk.X, pady=10, padx=5)

        self.region_entry = ttk.Entry(region_frame)
        self.region_entry.pack(fill=tk.X, padx=5, pady=5)
        self.region_entry.insert(0, "0,0,800,600")

        ttk.Label(region_frame, text="Format: x1,y1,x2,y2").pack()

        # Key binding for stop (Escape key)
        self.root.bind('<Escape>', lambda e: self.stop_all())

    def toggle_learning(self):
        if not self.is_learning:
            try:
                # Parse region
                region = tuple(map(int, self.region_entry.get().split(',')))
                if len(region) != 4:
                    raise ValueError("Invalid region format")

                print(f"Starting learning mode with region: {region}")
                self.is_learning = True
                self.learn_button.configure(text="Stop Learning")
                self.start_button.state(['disabled'])
                self.status_label.configure(text="Status: Learning from gameplay...")

                # Start the AI in learning mode
                self.ai_bot.start_learning(region)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start learning: {str(e)}")
                self.status_label.configure(text=f"Error: {str(e)}")
        else:
            self.stop_learning()

    def stop_learning(self):
        if self.is_learning:
            print("Stopping learning mode")
            self.ai_bot.stop_learning()
            self.is_learning = False
            self.learn_button.configure(text="Learn from Gameplay")
            self.start_button.state(['!disabled'])
            self.status_label.configure(text="Status: Learning stopped")

    def start_ai(self):
        if not self.is_running:
            try:
                region = tuple(map(int, self.region_entry.get().split(',')))
                if len(region) != 4:
                    raise ValueError("Invalid region format")

                print("Starting AI control")
                self.is_running = True
                self.start_button.configure(text="Stop AI")
                self.learn_button.state(['disabled'])
                self.status_label.configure(text="Status: AI Control active...")

                # Start AI control in a separate thread
                self.ai_thread = threading.Thread(target=self.run_ai_loop)
                self.ai_thread.daemon = True
                self.ai_thread.start()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start AI: {str(e)}")
                self.status_label.configure(text=f"Error: {str(e)}")
        else:
            self.stop_ai()

    def stop_ai(self):
        if self.is_running:
            print("Stopping AI control")
            self.is_running = False
            self.start_button.configure(text="Start AI Control")
            self.learn_button.state(['!disabled'])
            self.status_label.configure(text="Status: AI Control stopped")

    def stop_all(self):
        print("Stopping all operations")
        self.stop_learning()
        self.stop_ai()
        self.status_label.configure(text="Status: All operations stopped")

    def run_ai_loop(self):
        """Main AI control loop"""
        print("Starting AI control loop")
        while self.is_running:
            try:
                # Update game environment
                self.game_env.update()

                # Get current game state
                current_position = self.game_env.player_position
                nearby_objects = self.game_env.get_nearby_objects(current_position, radius=20)

                # Create game state
                game_state = {
                    'player_position': current_position,
                    'nearby_objects': nearby_objects,
                    'player_status': {'health': 100, 'energy': 100}
                }

                # Let AI decide and execute action
                self.ai_bot.observe_environment(game_state)
                action = self.ai_bot.decide_action(game_state)

                # Execute action
                if action['action'] != 'explore':
                    outcome = self.game_env.interact_with_object(action['target'])
                    self.ai_bot.learn_from_outcome(action, outcome)

                time.sleep(0.1)  # Prevent excessive CPU usage
            except Exception as e:
                print(f"Error in AI loop: {e}")
                time.sleep(1)  # Wait longer on error

    def run(self):
        """Start the application"""
        print("Starting Game AI Interface")
        self.root.mainloop()

def main():
    app = GameAIInterface()
    app.run()

if __name__ == "__main__":
    main()