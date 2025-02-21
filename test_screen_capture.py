from PIL import ImageGrab
import numpy as np
import time
import sys

def test_screen_capture(region=(0, 0, 800, 600), duration=10):
    """Test screen capture functionality for a specified duration."""
    print(f"Starting screen capture test with region: {region}")
    print(f"Test will run for {duration} seconds")
    
    frames_captured = 0
    start_time = time.time()
    last_fps_check = start_time
    
    try:
        while time.time() - start_time < duration:
            capture_start = time.time()
            
            # Attempt screen capture
            with ImageGrab.grab(bbox=region) as screen:
                frame = np.array(screen)
                frames_captured += 1
                
                # Calculate some basic metrics
                capture_time = time.time() - capture_start
                current_time = time.time()
                
                if current_time - last_fps_check >= 1:  # Report every second
                    fps = frames_captured / (current_time - last_fps_check)
                    print(f"Capture stats - FPS: {fps:.1f}, Frame time: {capture_time*1000:.1f}ms")
                    print(f"Frame shape: {frame.shape}, Mean brightness: {frame.mean():.1f}")
                    frames_captured = 0
                    last_fps_check = current_time
                
                time.sleep(max(0, 1/30 - capture_time))  # Cap at 30 FPS
                
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error during capture: {e}")
        raise
    
    print("Screen capture test completed successfully")

if __name__ == "__main__":
    try:
        # Parse region from command line if provided
        if len(sys.argv) > 4:
            region = tuple(map(int, sys.argv[1:5]))
        else:
            region = (0, 0, 800, 600)
        
        test_screen_capture(region=region)
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
