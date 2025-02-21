import os
import tkinter as tk
from tkinter import ttk, messagebox
from game_environment import GameEnvironment
from ai_core import AIBot
import threading
import time
import traceback
from typing import Dict

class GameAIInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Game AI Learning Interface")
        self.root.geometry("800x600")
        self.setup_ui()

        print("Initializing game environment...")
        self.game_env = GameEnvironment()
        print("Initializing AI bot...")
        self.ai_bot = AIBot()

        self.is_running = False
        self.is_learning = False

        # Schedule auto-test for headless environment
        self.root.after(2000, self._auto_test)

    def setup_ui(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title and description
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(title_frame, text="Game AI Learning System", 
                 font=('Helvetica', 16, 'bold')).pack()
        ttk.Label(title_frame, 
                 text="Click 'Learn' and play the game in the specified window region.\n" +
                      "The AI will observe and learn from your gameplay.\n" +
                      "Press ESC or Stop to end the current operation.",
                 wraplength=700).pack()

        # Status frame with more detailed information
        self.status_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        self.status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Add debug checkbox
        self.debug_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.status_frame, text="Show Debug Info", 
                       variable=self.debug_var).pack(anchor=tk.W)

        self.status_text = tk.Text(self.status_frame, height=15, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add scrollbar to status text
        scrollbar = ttk.Scrollbar(self.status_frame, orient=tk.VERTICAL, 
                                command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.configure(yscrollcommand=scrollbar.set)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        # Control buttons with improved styling
        self.learn_button = ttk.Button(button_frame, text="Learn from Gameplay", 
                                    command=self._safe_toggle_learning)
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

        ttk.Label(region_frame, 
                text="Format: x1,y1,x2,y2 (coordinates of the game window area to capture)").pack()

        # Key binding for stop (Escape key)
        self.root.bind('<Escape>', lambda e: self.stop_all())

        # Add test key binding for debugging (Ctrl+L to simulate Learn button click)
        self.root.bind('<Control-l>', lambda e: self._test_learn_button())

        # Debug print on initialization
        print("\nUI Initialization complete")
        print("Debug controls:")
        print("- Ctrl+L: Simulate Learn button click")
        print("- Escape: Stop all operations")

        # Initialize system status
        self.update_status("System initialized", "Ready to start learning or AI control", clear=True)

    def _test_learn_button(self):
        """Debug function to test Learn button functionality"""
        print("\nTest: Simulating Learn button click")
        self._safe_toggle_learning()

    def _safe_toggle_learning(self):
        """Thread-safe wrapper for toggle_learning"""
        try:
            print("\nLearn button clicked - Executing safe toggle...")
            # Force an immediate GUI update
            self.root.update_idletasks()
            # Execute in the main thread
            self._execute_toggle_learning()
        except Exception as e:
            error_msg = f"Critical error in button handler: {e}\n{traceback.format_exc()}"
            print(error_msg)
            messagebox.showerror("Critical Error", str(e))

    def _execute_toggle_learning(self):
        """Execute toggle_learning in the main thread"""
        try:
            print("Executing toggle_learning in main thread")
            self.toggle_learning()
        except Exception as e:
            error_msg = f"Error in toggle execution: {e}\n{traceback.format_exc()}"
            print(error_msg)
            self.update_status("Error", error_msg)

    def update_status(self, status: str, details: str = "", clear: bool = False):
        """Update status with optional details"""
        try:
            if clear:
                self.status_text.delete(1.0, tk.END)

            timestamp = time.strftime("%H:%M:%S")
            status_msg = f"[{timestamp}] {status}"
            if details:
                status_msg += f"\n{details}\n"
            else:
                status_msg += "\n"

            print(f"\nStatus Update: {status_msg.strip()}")
            # Use after to ensure thread-safe update
            self.root.after(0, lambda: self._safe_text_update(status_msg))

        except Exception as e:
            print(f"Error updating status: {e}")

    def _safe_text_update(self, text: str):
        """Thread-safe text widget update"""
        try:
            self.status_text.insert(tk.END, text)
            self.status_text.see(tk.END)
            self.root.update_idletasks()
        except Exception as e:
            print(f"Error in safe text update: {e}")

    def toggle_learning(self):
        if not self.is_learning:
            try:
                print("\nLearn button pressed - Starting learning mode...")
                # Parse region
                region_str = self.region_entry.get().strip()
                try:
                    region = tuple(map(int, region_str.split(',')))
                    if len(region) != 4:
                        raise ValueError
                    if region[0] >= region[2] or region[1] >= region[3]:
                        raise ValueError("Invalid region dimensions")
                except:
                    raise ValueError(
                        "Invalid region format. Please use four numbers separated by commas (x1,y1,x2,y2)")

                self.update_status("Starting learning mode...", 
                                "Initializing screen capture and testing display access...", clear=True)

                def observation_callback(analysis: Dict):
                    """Callback to handle screen observations"""
                    try:
                        frame_data = analysis.get('frame_data', {})
                        movement = frame_data.get('movement_value', 0)
                        frame_size = frame_data.get('frame_size', (0, 0))
                        brightness = frame_data.get('brightness', 0)

                        if self.debug_var.get():
                            details = (
                                f"Screen Analysis Debug Info:\n"
                                f"• Capture Region: {region}\n"
                                f"• Frame Size: {frame_size}\n"
                                f"• Movement Detected: {movement:.1f}\n"
                                f"• Brightness: {brightness:.1f}\n"
                                f"• Status: {self.ai_bot.current_state}\n"
                                f"• Analysis Timestamp: {time.strftime('%H:%M:%S')}\n"
                            )
                            print(f"\nDebug: Received frame analysis:\n{details}")
                        else:
                            details = f"Learning from gameplay... Movement: {movement:.1f}"

                        # Use after() to ensure thread-safe UI updates
                        self.root.after(100, lambda: self.update_status(
                            "Learning in Progress", details))

                    except Exception as e:
                        error_msg = f"Callback error: {e}\n{traceback.format_exc()}"
                        print(error_msg)
                        self.root.after(100, lambda: self.update_status(
                            "Warning", f"Observation error: {str(e)}"))

                print("Setting up observation callback...")
                # Set the callback before starting learning
                self.ai_bot.screen_observer.callback = observation_callback

                # Start the AI in learning mode with additional error handling
                try:
                    print("Attempting to start learning mode...")
                    self.ai_bot.start_learning(region)
                    print("Learning mode started successfully")
                except Exception as e:
                    error_msg = f"Failed to start learning mode: {e}\n{traceback.format_exc()}"
                    print(error_msg)
                    raise Exception(f"Screen capture initialization failed: {e}")

                self.is_learning = True
                self.learn_button.configure(text="Stop Learning")
                self.start_button.state(['disabled'])
                self.update_status("Learning mode active", 
                                "Screen observation started successfully")

            except Exception as e:
                error_details = f"Error starting learning mode: {str(e)}\n{traceback.format_exc()}"
                print(error_details)
                messagebox.showerror("Error", f"Failed to start learning: {str(e)}")
                self.update_status("Error", error_details)
        else:
            self.stop_learning()

    def _auto_test(self):
        """Automatically test button functionality in headless mode"""
        print("\nAuto-test: Simulating Learn button click...")
        try:
            self._safe_toggle_learning()
        except Exception as e:
            print(f"Auto-test error: {e}")
            traceback.print_exc()


    def stop_learning(self):
        if self.is_learning:
            self.update_status("Stopping learning mode...")
            try:
                self.ai_bot.stop_learning()
                print("Learning mode stopped successfully")
            except Exception as e:
                print(f"Error stopping learning mode: {e}")
            finally:
                self.is_learning = False
                self.learn_button.configure(text="Learn from Gameplay")
                self.start_button.state(['!disabled'])
                self.update_status("Learning stopped", "Ready to start AI control")

    def start_ai(self):
        if not self.is_running:
            try:
                region_str = self.region_entry.get().strip()
                try:
                    region = tuple(map(int, region_str.split(',')))
                    if len(region) != 4:
                        raise ValueError
                except:
                    raise ValueError(
                        "Invalid region format. Please use four numbers separated by commas (x1,y1,x2,y2)")

                self.update_status("Starting AI control...", 
                               "Initializing AI systems", clear=True)

                self.is_running = True
                self.start_button.configure(text="Stop AI")
                self.learn_button.state(['disabled'])

                # Start AI control in a separate thread
                self.ai_thread = threading.Thread(target=self.run_ai_loop)
                self.ai_thread.daemon = True
                self.ai_thread.start()

            except Exception as e:
                error_details = f"Error: {str(e)}\n{traceback.format_exc()}"
                print(error_details)
                messagebox.showerror("Error", f"Failed to start AI: {str(e)}")
                self.update_status("Error", error_details)
        else:
            self.stop_ai()

    def stop_ai(self):
        if self.is_running:
            self.update_status("Stopping AI control...")
            try:
                self.is_running = False
                print("AI control stopped successfully")
            finally:
                self.start_button.configure(text="Start AI Control")
                self.learn_button.state(['!disabled'])
                self.update_status("AI Control stopped", "Ready to learn or start AI")

    def stop_all(self):
        print("Stopping all operations")
        self.stop_learning()
        self.stop_ai()
        self.update_status("All operations stopped", 
                          "Press 'Learn' to observe gameplay or 'Start AI' to begin AI control")

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

                # Let AI observe and decide action
                observation_data = self.ai_bot.observe_environment(game_state)
                if observation_data:  # Only process if we have valid observation data
                    self.ai_bot._handle_observation(observation_data)
                    action = self.ai_bot.decide_action(game_state)

                    # Execute action if it's not just exploration
                    if action and isinstance(action.get('target'), GameObject):
                        outcome = self.game_env.interact_with_object(action['target'])
                        if outcome:
                            self.ai_bot.learn_from_outcome(action, outcome)
                            self.update_status("AI Control active", 
                                             f"Action: {action['action']}, Outcome: {outcome}")

                time.sleep(0.1)  # Prevent excessive CPU usage
            except Exception as e:
                error_details = f"Error in AI loop: {e}\n{traceback.format_exc()}"
                print(error_details)
                self.update_status("AI Control error", error_details)
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