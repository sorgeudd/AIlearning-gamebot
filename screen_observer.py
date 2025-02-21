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

        # Create a virtual test frame with more dynamic content
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
        """Update virtual frame with dynamic content"""
        if self._virtual_frame is None:
            return

        # Clear frame
        self._virtual_frame.fill(0)

        # Add timestamp and dynamic elements
        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(self._virtual_frame, f'AI Learning Mode - {timestamp}',
                   (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1,
                   (255, 255, 255), 2)

        # Add simulated game objects (moving dots)
        t = time.time()
        for i in range(5):
            x = int(320 + 100 * np.sin(t + i))
            y = int(240 + 100 * np.cos(t + i))
            cv2.circle(self._virtual_frame, (x, y), 5, (0, 255, 0), -1)

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

    # Rest of the file remains unchanged
