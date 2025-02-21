import time
import threading
from typing import Dict, List, Tuple, Callable, Optional
from PIL import ImageGrab, Image
import numpy as np
from numpy.typing import NDArray
import traceback

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
        print("Screen Observer initialized for VNC display")

    def start_observation(self, region: Optional[Tuple[int, int, int, int]] = None) -> None:
        """Start observing the game window"""
        try:
            print(f"Starting screen observation with region: {region}")

            # Default to full screen if no region specified
            if not region:
                region = (0, 0, 800, 600)

            # Test capture to verify VNC access
            try:
                test_capture = ImageGrab.grab(bbox=region)
                test_array = np.array(test_capture)
                test_capture.close()

                if test_array.mean() == 0:
                    print("Note: Initial capture shows empty screen - this is normal for VNC initialization")

                print(f"Screen capture test successful - Size: {test_array.shape}")
            except Exception as e:
                raise Exception(f"Failed to capture screen: {e}. Ensure VNC display is active.")

            self.is_recording = True
            self.region = region
            self._error_count = 0
            self._frames_captured = 0
            self._last_fps_check = time.time()
            self._last_frame_time = time.time()

            # Start capture thread
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()

            print("Screen observation started successfully")
        except Exception as e:
            error_msg = f"Failed to start screen observation: {e}\n{traceback.format_exc()}"
            print(error_msg)
            raise Exception(error_msg)

    def _capture_loop(self) -> None:
        """Main screen capture loop"""
        print("Starting screen capture loop in VNC environment")
        while self.is_recording:
            try:
                current_time = time.time()
                frame_delta = current_time - self._last_frame_time

                # Capture screen region
                with ImageGrab.grab(bbox=self.region) as screen:
                    screen_array = np.array(screen)

                    # Skip empty frames (common in VNC during initialization)
                    if screen_array.mean() == 0 and self._frames_captured < 5:
                        print("Warning: Empty frame detected, waiting for VNC to initialize...")
                        time.sleep(0.5)
                        continue

                    capture_time = time.time() - current_time

                    self._analyze_frame(screen_array)
                    self._frames_captured += 1
                    self._error_count = 0
                    self._last_frame_time = current_time

                    # Log performance metrics every 5 seconds
                    if current_time - self._last_fps_check >= 5:
                        fps = self._frames_captured / (current_time - self._last_fps_check)
                        print(f"Capture stats - FPS: {fps:.1f}, Frame time: {capture_time*1000:.1f}ms")
                        self._frames_captured = 0
                        self._last_fps_check = current_time

                # Cap at 30 FPS
                time.sleep(max(0, 1/30 - capture_time))

            except Exception as e:
                self._error_count += 1
                print(f"Screen capture error ({self._error_count}/{self._max_errors}): {e}")
                if self._error_count >= self._max_errors:
                    print("Too many screen capture errors, stopping observation")
                    self.is_recording = False
                    break
                time.sleep(1)

    def _analyze_frame(self, frame: NDArray) -> None:
        """Analyze the current frame for gameplay patterns"""
        try:
            # Calculate basic metrics
            brightness = float(np.mean(frame))
            movement = 0.0

            if self.last_frame is not None:
                # Calculate movement by comparing with last frame
                diff = np.abs(frame - self.last_frame)
                movement = float(np.mean(diff))

            self.last_frame = frame.copy()

            # Send analysis to callback
            self.callback({
                'timestamp': time.time(),
                'frame_data': {
                    'brightness': brightness,
                    'movement_detected': movement > 10.0,
                    'movement_value': movement,
                    'frame_size': frame.shape,
                    'region': self.region
                }
            })

        except Exception as e:
            print(f"Frame analysis error: {e}")
            print(traceback.format_exc())

    def stop_observation(self) -> None:
        """Stop observing the game window"""
        print("Stopping screen observation...")
        self.is_recording = False
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join(timeout=1.0)
        print(f"Screen observation stopped. Total frames captured: {self._frames_captured}")

    def get_region(self) -> Optional[Tuple[int, int, int, int]]:
        """Return the current observation region"""
        return self.region