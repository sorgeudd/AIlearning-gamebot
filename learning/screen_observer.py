import time
import threading
from typing import Dict, List, Tuple, Callable, Optional
from PIL import ImageGrab
import numpy as np
from numpy.typing import NDArray

class ScreenObserver:
    def __init__(self, callback: Callable[[Dict], None]):
        self.is_recording = False
        self.callback = callback
        self.region: Optional[Tuple[int, int, int, int]] = None
        self.last_frame: Optional[NDArray] = None

    def start_observation(self, region: Optional[Tuple[int, int, int, int]] = None) -> None:
        """Start observing the game window"""
        self.is_recording = True
        self.region = region

        # Start screen capture thread
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()

    def stop_observation(self) -> None:
        """Stop observing the game window"""
        self.is_recording = False
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join()

    def _capture_loop(self) -> None:
        """Main screen capture loop"""
        while self.is_recording:
            try:
                # Capture screen region
                screen = ImageGrab.grab(bbox=self.region)
                screen_array = np.array(screen)

                # Analyze current frame
                self._analyze_frame(screen_array)

                # Sleep to maintain reasonable CPU usage
                time.sleep(0.1)
            except Exception as e:
                print(f"Screen capture error: {e}")
                time.sleep(1)  # Wait longer on error

    def _analyze_frame(self, frame: NDArray) -> None:
        """Analyze the current frame for gameplay patterns"""
        try:
            # Calculate basic image statistics
            brightness = float(np.mean(frame))
            movement = 0.0

            if self.last_frame is not None:
                # Calculate movement by comparing with last frame
                diff = np.abs(frame - self.last_frame)
                movement = float(np.mean(diff))

            self.last_frame = frame

            # Create analysis data
            analysis = {
                'timestamp': time.time(),
                'frame_data': {
                    'brightness': brightness,
                    'movement_detected': movement > 10.0,
                    'frame_size': frame.shape
                }
            }

            # Send analysis to callback
            self.callback(analysis)

        except Exception as e:
            print(f"Frame analysis error: {e}")

    def get_region(self) -> Tuple[int, int, int, int]:
        """Return the current observation region"""
        return self.region or (0, 0, 800, 600)