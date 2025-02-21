import os
import time
import traceback
from typing import Dict
from game_environment import GameEnvironment, GameObject
from ai_core import AIBot

class GameAIHeadless:
    def __init__(self):
        self.is_running = False
        self.is_learning = False
        self.debug_enabled = True

        print("Initializing game environment...")
        self.game_env = GameEnvironment()
        print("Initializing AI bot...")
        self.ai_bot = AIBot()

        # Auto-start learning mode
        self._auto_start()

    def _auto_start(self):
        """Automatically start the learning process"""
        print("\nAuto-starting AI learning mode...")
        try:
            self.start_learning()
        except Exception as e:
            print(f"Auto-start error: {e}")
            traceback.print_exc()

    def update_status(self, status: str, details: str = ""):
        """Print status updates to console"""
        timestamp = time.strftime("%H:%M:%S")
        status_msg = f"[{timestamp}] {status}"
        if details:
            status_msg += f"\n{details}"
        print(status_msg)

    def start_learning(self):
        if not self.is_learning:
            try:
                print("\nStarting learning mode...")
                # Use a default region for virtual frame generation
                region = (0, 0, 800, 600)

                def observation_callback(analysis: Dict):
                    """Handle screen observations"""
                    try:
                        frame_data = analysis.get('frame_data', {})
                        movement = frame_data.get('movement_value', 0)
                        frame_size = frame_data.get('frame_size', (0, 0))
                        brightness = frame_data.get('brightness', 0)

                        if self.debug_enabled:
                            details = (
                                f"Screen Analysis:\n"
                                f"• Frame Size: {frame_size}\n"
                                f"• Movement: {movement:.1f}\n"
                                f"• Brightness: {brightness:.1f}\n"
                                f"• Bot State: {self.ai_bot.current_state}\n"
                            )
                            print(f"\n{details}")
                    except Exception as e:
                        print(f"Callback error: {e}")

                # Set the callback before starting learning
                self.ai_bot.screen_observer.callback = observation_callback

                # Start the AI in learning mode
                self.ai_bot.start_learning(region)
                self.is_learning = True
                self.update_status("Learning mode active", "Screen observation started")

            except Exception as e:
                error_details = f"Error starting learning mode: {str(e)}\n{traceback.format_exc()}"
                print(error_details)
                raise

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
                self.update_status("Learning stopped", "Ready to start AI control")

def main():
    app = GameAIHeadless()
    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        print("\nShutting down...")
        app.stop_learning()

if __name__ == "__main__":
    main()