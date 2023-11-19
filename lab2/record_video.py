import cv2

def record_video(output_file):
    # Check if the video capture device is available
    video = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Set specially for Windows

    # Check if the video capture device is opened successfully
    if not video.isOpened():
        print("Error: Could not open video capture device")
        return

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Changed to lowercase for cross-platform compatibility
    fps = 20.0  # Frames per second
    resolution = (720, 480)
    result = cv2.VideoWriter(output_file, fourcc, fps, resolution)

    try:
        while True:
            ret, frame = video.read()

            if ret:
                result.write(frame)
                cv2.imshow('Recording', frame)

                # Break the loop if 'q' is pressed
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            else:
                break
    finally:
        # Release resources
        video.release()
        result.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    output_filename = 'vid.mp4'
    record_video(output_filename)
