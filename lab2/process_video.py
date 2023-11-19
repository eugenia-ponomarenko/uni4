import cv2

def process_video(video_file):
    cap = cv2.VideoCapture(video_file)

    if not cap.isOpened():
        print("Error: Could not open video file")
        return

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        resized_frame = cv2.resize(frame, (720, 480))
        gray = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('Video', gray)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


process_video('lab2.mp4')