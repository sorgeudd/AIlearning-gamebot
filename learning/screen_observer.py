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
        print("Screen Observer initialized")

    def start_observation(self, region: Optional[Tuple[int, int, int, int]] = None) -> None:
        """Start observing the game window"""
        try:
            print(f"Attempting to start screen observation with region: {region}")

            # Validate region
            if region:
                if not all(isinstance(x, int) for x in region):
                    raise ValueError("All region coordinates must be integers")
                if len(region) != 4:
                    raise ValueError("Region must be a tuple of 4 integers (x1,y1,x2,y2)")
                if region[0] >= region[2] or region[1] >= region[3]:
                    raise ValueError("Invalid region dimensions (x1 must be < x2 and y1 must be < y2)")

            print("Region validation passed")

            # Test capture to verify permissions and region validity
            test_capture = ImageGrab.grab(bbox=region)
            test_size = test_capture.size
            test_capture.close()
            print(f"Test screen capture successful - Capture size: {test_size}")

            self.is_recording = True
            self.region = region
            self._error_count = 0
            self._frames_captured = 0
            self._last_fps_check = time.time()
            self._last_frame_time = time.time()

            # Start screen capture thread
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()

            print(f"Screen observation started successfully")
        except Exception as e:
            error_msg = f"Failed to start screen observation: {e}\n{traceback.format_exc()}"
            print(error_msg)
            raise Exception(error_msg)

    def stop_observation(self) -> None:
        """Stop observing the game window"""
        print("Stopping screen observation...")
        self.is_recording = False
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join(timeout=1.0)
        print(f"Screen observation stopped. Total frames captured: {self._frames_captured}")

    def _capture_loop(self) -> None:
        """Main screen capture loop"""
        print("Starting screen capture loop")
        while self.is_recording:
            try:
                current_time = time.time()
                frame_delta = current_time - self._last_frame_time

                # Capture screen region
                with ImageGrab.grab(bbox=self.region) as screen:
                    screen_array = np.array(screen)
                    capture_time = time.time() - current_time
                    print(f"Frame captured in {capture_time*1000:.1f}ms")

                    self._analyze_frame(screen_array)
                    self._frames_captured += 1
                    self._error_count = 0  # Reset error count on successful capture
                    self._last_frame_time = current_time

                    # Calculate and log FPS every 5 seconds
                    if current_time - self._last_fps_check >= 5:
                        fps = self._frames_captured / (current_time - self._last_fps_check)
                        print(f"Screen capture performance - FPS: {fps:.2f}, Frame time: {frame_delta*1000:.1f}ms")
                        self._frames_captured = 0
                        self._last_fps_check = current_time

                # Sleep to maintain reasonable CPU usage (aim for ~30 FPS)
                target_frame_time = 1.0 / 30
                sleep_time = max(0, target_frame_time - (time.time() - current_time))
                time.sleep(sleep_time)

            except Exception as e:
                self._error_count += 1
                print(f"Screen capture error ({self._error_count}/{self._max_errors}): {e}")
                print(traceback.format_exc())

                if self._error_count >= self._max_errors:
                    print("Too many screen capture errors, stopping observation")
                    self.is_recording = False
                    break

                time.sleep(1)  # Wait longer on error

    def _analyze_frame(self, frame: NDArray) -> None:
        """Analyze the current frame for gameplay patterns"""
        try:
            start_time = time.time()

            # Calculate basic image statistics
            brightness = float(np.mean(frame))
            movement = 0.0

            if self.last_frame is not None:
                # Calculate movement by comparing with last frame
                diff = np.abs(frame - self.last_frame)
                movement = float(np.mean(diff))

            self.last_frame = frame.copy()

            # Create analysis data
            analysis = {
                'timestamp': time.time(),
                'frame_data': {
                    'brightness': brightness,
                    'movement_detected': movement > 10.0,
                    'movement_value': movement,
                    'frame_size': frame.shape,
                    'region': self.region,
                    'frames_captured': self._frames_captured,
                    'analysis_time': (time.time() - start_time) * 1000  # in milliseconds
                }
            }

            print(f"Frame analyzed - Movement: {movement:.1f}, Analysis time: {analysis['frame_data']['analysis_time']:.1f}ms")

            # Send analysis to callback
            self.callback(analysis)

        except Exception as e:
            print(f"Frame analysis error: {e}")
            print(traceback.format_exc())

    def get_region(self) -> Optional[Tuple[int, int, int, int]]:
        """Return the current observation region"""
        return self.region