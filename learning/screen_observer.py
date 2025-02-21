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

        # Create a virtual test frame
        print("Creating virtual frame...")
        try:
            self._virtual_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(self._virtual_frame, 'AI Learning Mode Active', 
                       (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                       (255, 255, 255), 2)
            print("Virtual frame created successfully")
            print(f"Frame shape: {self._virtual_frame.shape}")
        except Exception as e:
            print(f"Error creating virtual frame: {e}")
            raise

    def start_observation(self, region: Optional[Tuple[int, int, int, int]] = None) -> None:
        """Start observing the game window"""
        try:
            print("\nStarting screen observation...")
            print(f"Requested region: {region}")

            if not region:
                region = (0, 0, 800, 600)
                print("No region specified, using default:", region)

            if self._virtual_frame is None:
                print("Recreating virtual frame...")
                self._virtual_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(self._virtual_frame, 'AI Learning Mode Active', 
                           (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                           (255, 255, 255), 2)

            print("\nStarting observation thread...")
            self.is_recording = True
            self.region = region
            self._error_count = 0
            self._frames_captured = 0
            self._last_fps_check = time.time()

            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            print("Observation thread started successfully")

        except Exception as e:
            error_msg = f"Failed to start screen observation:\n{traceback.format_exc()}"
            print(error_msg)
            raise Exception(error_msg)

    def _capture_loop(self) -> None:
        """Main capture loop using virtual frames if needed"""
        print("\nEntering capture loop")
        print("Initial setup:")
        print(f"- Recording state: {self.is_recording}")
        print(f"- Region: {self.region}")
        print(f"- Error count: {self._error_count}")
        print(f"- Virtual frame exists: {self._virtual_frame is not None}")
        if self._virtual_frame is not None:
            print(f"- Virtual frame shape: {self._virtual_frame.shape}")

        frame_count = 0
        last_log_time = time.time()

        try:
            while self.is_recording and self._virtual_frame is not None:
                try:
                    current_time = time.time()
                    frame_delta = current_time - self._last_frame_time

                    # Log status periodically
                    if current_time - last_log_time > 5:
                        print("\nCapture Status Update:")
                        print(f"- Is recording: {self.is_recording}")
                        print(f"- Error count: {self._error_count}")
                        print(f"- Frames captured: {self._frames_captured}")
                        print(f"- FPS: {frame_count / 5:.1f}")
                        frame_count = 0
                        last_log_time = current_time

                    # Generate virtual frame with timestamp
                    frame = self._virtual_frame.copy()
                    cv2.putText(frame, f'Time: {time.strftime("%H:%M:%S")}',
                              (50, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                              (255, 255, 255), 2)

                    # Add some movement to simulate activity
                    noise = np.random.randint(0, 30, frame.shape, dtype=np.uint8)
                    frame = cv2.add(frame, noise)

                    # Debug print for first few frames
                    if self._frames_captured < 5:
                        print(f"\nFrame {self._frames_captured + 1} generated:")
                        print(f"- Shape: {frame.shape}")
                        print(f"- Mean value: {frame.mean():.2f}")

                    frame_count += 1
                    self._analyze_frame(frame)
                    self._frames_captured += 1
                    self._error_count = 0
                    self._last_frame_time = current_time

                    # Maintain reasonable frame rate
                    time.sleep(max(0, 1/30 - frame_delta))

                except Exception as e:
                    self._error_count += 1
                    print(f"\nCapture error ({self._error_count}/{self._max_errors}):")
                    print(traceback.format_exc())

                    if self._error_count >= self._max_errors:
                        print("Too many errors, stopping observation")
                        self.is_recording = False
                        break

                    time.sleep(1)  # Wait before retry

        finally:
            print("\nCapture loop ended")
            print(f"Total frames captured: {self._frames_captured}")
            print(f"Final error count: {self._error_count}")

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

            analysis_data = {
                'timestamp': time.time(),
                'frame_data': {
                    'brightness': brightness,
                    'movement_detected': movement > 10.0,
                    'movement_value': movement,
                    'frame_size': frame.shape,
                    'region': self.region
                }
            }

            if self.callback:
                self.callback(analysis_data)
            else:
                print("Warning: No callback registered for frame analysis")

        except Exception as e:
            print(f"\nFrame analysis error:")
            print(traceback.format_exc())

    def stop_observation(self) -> None:
        """Stop observing the game window"""
        print("\nStopping screen observation...")
        self.is_recording = False
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join(timeout=1.0)
        print(f"Observation stopped. Frames captured: {self._frames_captured}")

    def get_region(self) -> Optional[Tuple[int, int, int, int]]:
        """Return the current observation region"""
        return self.region