import time
import threading
import os
import traceback
from typing import Dict, List, Tuple, Callable, Optional
import cv2
import numpy as np
from numpy.typing import NDArray

class ScreenObserver:
    def __init__(self, callback: Callable[[Dict], None]):
        self.is_recording = False
        self.callback = callback
        self.region: Optional[Tuple[int, int, int, int]] = None
        self.last_frame: Optional[NDArray] = None
        self._error_count = 0
        self._max_errors = 3
        self._frames_captured = 0
        self._last_fps_check = time.time()
        self._last_frame_time = 0
        self._virtual_frame = None
        print("\nScreen Observer initialized")
        print("Environment details:")
        print(f"- DISPLAY: {os.environ.get('DISPLAY', 'Not set')}")
        print(f"- PWD: {os.getcwd()}")

        # Create a virtual test frame with game-like elements
        print("Creating virtual frame...")
        try:
            self._virtual_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            self._update_virtual_frame()
            print("Virtual frame created successfully")
            print(f"Frame shape: {self._virtual_frame.shape}")
        except Exception as e:
            print(f"Error creating virtual frame: {e}")
            raise

    def _update_virtual_frame(self):
        """Update virtual frame with dynamic game-like content"""
        if self._virtual_frame is None:
            return

        # Clear frame
        self._virtual_frame.fill(0)

        # Add timestamp and status
        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(self._virtual_frame, f'AI Learning Mode - {timestamp}',
                   (50, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                   (255, 255, 255), 2)

        # Add simulated game objects
        t = time.time()

        # Player character (moving in a circle)
        player_x = int(320 + 100 * np.sin(t * 0.5))
        player_y = int(240 + 100 * np.cos(t * 0.5))
        cv2.circle(self._virtual_frame, (player_x, player_y), 10, (0, 255, 0), -1)

        # Resources (static positions)
        for i in range(3):
            x = int(100 + i * 200)
            y = int(100)
            cv2.rectangle(self._virtual_frame, (x-5, y-5), (x+5, y+5), (0, 255, 255), -1)
            cv2.putText(self._virtual_frame, 'Resource',
                       (x-30, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                       (255, 255, 255), 1)

        # Enemies (moving randomly)
        for i in range(2):
            x = int(150 + i * 300 + 20 * np.sin(t * (i + 1)))
            y = int(400 + 20 * np.cos(t * (i + 1)))
            cv2.circle(self._virtual_frame, (x, y), 8, (0, 0, 255), -1)
            cv2.putText(self._virtual_frame, 'Enemy',
                       (x-20, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                       (255, 255, 255), 1)

        # Status information
        cv2.putText(self._virtual_frame, f'FPS: {int(1/(time.time() - self._last_frame_time + 0.001))}',
                   (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                   (255, 255, 255), 1)
        cv2.putText(self._virtual_frame, f'Frames: {self._frames_captured}',
                   (120, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                   (255, 255, 255), 1)

    def _analyze_frame(self, frame: NDArray) -> None:
        """Analyze the current frame for gameplay patterns"""
        try:
            if frame is None:
                print("Warning: Received null frame in analysis")
                return

            brightness = float(np.mean(frame))
            movement = 0.0

            if self.last_frame is not None:
                if frame.shape == self.last_frame.shape:
                    diff = np.abs(frame - self.last_frame)
                    movement = float(np.mean(diff))

            self.last_frame = frame.copy()

            # Generate simulated game objects for testing state transitions
            game_objects = []
            if movement > 0.1:  # If there's movement, add some virtual objects
                game_objects.extend([
                    {'type': 'resource', 'position': (100, 100), 'properties': {'resource_type': 'wood'}},
                    {'type': 'fishing_spot', 'position': (200, 200), 'properties': {'fish_type': 'common'}},
                    {'type': 'enemy', 'position': (300, 300), 'properties': {'level': 3, 'health': 100}}
                ])

            analysis_data = {
                'timestamp': time.time(),
                'frame_data': {
                    'brightness': brightness,
                    'movement_detected': movement > 10.0,
                    'movement_value': movement,
                    'frame_size': frame.shape,
                    'region': self.region
                },
                'nearby_objects': game_objects,
                'player_status': {
                    'health': 80,  # Simulated player health
                    'position': (150, 150)
                }
            }

            if self.callback:
                self.callback(analysis_data)

        except Exception as e:
            print(f"\nFrame analysis error:")
            print(traceback.format_exc())

    def start_observation(self, region: Optional[Tuple[int, int, int, int]] = None) -> None:
        """Start observing the game window"""
        try:
            print("\nStarting screen observation...")
            if not region:
                region = (0, 0, 800, 600)

            self.is_recording = True
            self.region = region
            self._error_count = 0
            self._frames_captured = 0
            self._last_fps_check = time.time()

            # Start capture thread
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            print("Observation thread started successfully")

        except Exception as e:
            error_msg = f"Failed to start screen observation:\n{traceback.format_exc()}"
            print(error_msg)
            raise Exception(f"Screen capture initialization failed: {e}")

    def _capture_loop(self) -> None:
        """Main capture loop using virtual frames"""
        print("\nEntering capture loop")
        frame_count = 0
        last_log_time = time.time()

        try:
            while self.is_recording and self._virtual_frame is not None:
                try:
                    current_time = time.time()
                    frame_delta = current_time - self._last_frame_time

                    # Update virtual frame with dynamic content
                    self._update_virtual_frame()
                    frame = self._virtual_frame.copy()

                    if self._frames_captured < 5:
                        print(f"\nFrame {self._frames_captured + 1} generated:")
                        print(f"- Shape: {frame.shape}")
                        print(f"- Mean value: {frame.mean():.2f}")

                    frame_count += 1
                    self._analyze_frame(frame)
                    self._frames_captured += 1
                    self._error_count = 0
                    self._last_frame_time = current_time

                    # Log status periodically
                    if current_time - last_log_time > 5:
                        print("\nCapture Status Update:")
                        print(f"- Is recording: {self.is_recording}")
                        print(f"- Frames captured: {self._frames_captured}")
                        print(f"- FPS: {frame_count / 5:.1f}")
                        frame_count = 0
                        last_log_time = current_time

                    # Maintain reasonable frame rate
                    time.sleep(max(0, 1/30 - frame_delta))

                except Exception as e:
                    print(f"\nFrame capture error: {e}")
                    traceback.print_exc()
                    time.sleep(1)  # Wait before retry

        except Exception as e:
            print(f"\nCapture loop error: {e}")
            traceback.print_exc()
        finally:
            print("\nCapture loop ended")
            print(f"Total frames captured: {self._frames_captured}")

    def stop_observation(self) -> None:
        """Stop observing the game window"""
        print("\nStopping screen observation...")
        self.is_recording = False
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join(timeout=1.0)
        print(f"Observation stopped. Total frames captured: {self._frames_captured}")

    def get_region(self) -> Optional[Tuple[int, int, int, int]]:
        """Return the current observation region"""
        return self.region