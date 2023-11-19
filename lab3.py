import cv2
import numpy as np

class ObjectTracker(object):
    def __init__(self, scaling_factor=1.5):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.scaling_factor = scaling_factor
        cv2.namedWindow('Object Tracker')
        cv2.setMouseCallback('Object Tracker', self.mouse_event)
        self.selection = None
        self.drag_start = None
        self.tracking_state = 0
        self.tracker = None

    def mouse_event(self, event, x, y, flags, param):
        x, y = np.int16([x, y])
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
            self.tracking_state = 0
        if self.drag_start:
            if flags & cv2.EVENT_FLAG_LBUTTON:
                h, w = self.frame.shape[:2]
                xi, yi = self.drag_start
                x0, y0 = np.maximum(0, np.minimum([xi, yi], [x, y]))
                x1, y1 = np.minimum([w, h], np.maximum([xi, yi], [x, y]))
                self.selection = None
                if x1 - x0 > 0 and y1 - y0 > 0:
                    self.selection = (x0, y0, x1, y1)
            else:
                self.drag_start = None
                if self.selection is not None:
                    self.tracking_state = 1

    def start_tracking(self):
        while True:
            _, self.frame = self.cap.read()
            if self.frame is None:
                break

            if self.scaling_factor == 0:
                print("Error: Scaling factor (fx and fy) is set to zero. Please use a valid scaling factor.")
                break

            self.frame = cv2.resize(self.frame, None, fx=self.scaling_factor, fy=self.scaling_factor, interpolation=cv2.INTER_AREA)
            vis = self.frame.copy()

            if self.selection:
                x0, y0, x1, y1 = self.selection
                x0, y0, x1, y1 = max(0, x0), max(0, y0), min(x1, self.frame.shape[1]), min(y1, self.frame.shape[0])

                # Check if the adjusted ROI is valid
                if x1 > x0 and y1 > y0:
                    self.tracker = cv2.TrackerCSRT_create()
                    self.tracker.init(self.frame, (x0, y0, x1 - x0, y1 - y0))
                    self.selection = None
                else:
                    print("Invalid ROI, please try again.")

            if self.tracking_state == 1 and self.tracker:
                success, self.track_window = self.tracker.update(self.frame)
                if success:
                    x, y, w, h = map(int, self.track_window)
                    cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.imshow('Object Tracker', vis)
            c = cv2.waitKey(5)
            if c == ord('q'):
                break

        cv2.destroyAllWindows()

if __name__ == '__main__':
    ObjectTracker().start_tracking()