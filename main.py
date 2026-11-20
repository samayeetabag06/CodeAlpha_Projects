import cv2
import time
import argparse
from collections import defaultdict
from ultralytics import YOLO

def parse_arguments():
    parser = argparse.ArgumentParser(description="Real-Time Object Detection & Tracking")
    parser.add_argument(
        "--source", 
        type=str, 
        default="0", 
        help="Video source: '0' for webcam or path to a video file (e.g., 'sample.mp4')"
    )
    parser.add_argument(
        "--model", 
        type=str, 
        default="yolov8n.pt", 
        help="Pre-trained YOLO model (yolov8n.pt is lightweight and fast)"
    )
    parser.add_argument(
        "--conf", 
        type=float, 
        default=0.45, 
        help="Confidence threshold (0.0 to 1.0)"
    )
    return parser.parse_args()

def main():
    args = parse_arguments()

    # 1. Initialize YOLO Model with Pre-trained Weights
    print(f"[INFO] Loading YOLO model: {args.model}...")
    model = YOLO(args.model)

    # 2. Open Video Source (Webcam or File)
    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"[ERROR] Could not open video source: {args.source}")
        return

    # Set camera resolution (if using webcam)
    if isinstance(source, int):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Dictionary to store trajectory history (object_id -> list of centroid coordinates)
    track_history = defaultdict(lambda: [])

    # FPS Calculation Variables
    prev_time = 0
    
    print("\n" + "="*50)
    print(" 🚀 Object Detection & Tracking Started")
    print(" Controls:")
    print("  - Press 'q' to Exit")
    print("  - Press 's' to Save a Screenshot")
    print("="*50 + "\n")

    while True:
        success, frame = cap.read()
        if not success:
            print("[INFO] End of video stream or failed to grab frame.")
            break

        current_time = time.time()
        fps = 1 / (current_time - prev_time) if (current_time - prev_time) > 0 else 0
        prev_time = current_time

        # 3. Run Detection & Tracking (using ByteTrack algorithm)
        # persist=True retains tracks between consecutive frames
        results = model.track(
            source=frame, 
            persist=True, 
            conf=args.conf, 
            tracker="bytetrack.yaml", 
            verbose=False
        )

        active_track_count = 0

        # 4. Process Detections and Draw Bounding Boxes + Tracking IDs
        if results[0].boxes and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)
            class_ids = results[0].boxes.cls.cpu().numpy().astype(int)
            confidences = results[0].boxes.conf.cpu().numpy().astype(float)

            active_track_count = len(track_ids)

            for box, track_id, class_id, conf in zip(boxes, track_ids, class_ids, confidences):
                x1, y1, x2, y2 = box
                label = model.names[class_id]
                center_point = (int((x1 + x2) / 2), int((y1 + y2) / 2))

                # Store centroid for trajectory line
                track_history[track_id].append(center_point)
                if len(track_history[track_id]) > 30:  # Keep last 30 positions
                    track_history[track_id].pop(0)

                # Consistent color generation based on Tracking ID
                color = (
                    int((track_id * 37) % 255),
                    int((track_id * 73) % 255),
                    int((track_id * 109) % 255),
                )

                # Draw Bounding Box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                # Draw Label Pill: [ID: 5] person 88%
                caption = f"ID: {track_id} | {label} {conf:.0%}"
                (w, h), _ = cv2.getTextSize(caption, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
                cv2.rectangle(frame, (x1, y1 - 22), (x1 + w, y1), color, -1)
                cv2.putText(
                    frame, caption, (x1, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2
                )

                # Draw Trajectory / Motion Trail
                points = track_history[track_id]
                for i in range(1, len(points)):
                    thickness = int(1.5 * (i / len(points)) * 3) + 1
                    cv2.line(frame, points[i - 1], points[i], color, thickness)

        # 5. Draw Heads-Up Display (HUD)
        # Background overlay for status text
        cv2.rectangle(frame, (10, 10), (250, 80), (20, 20, 20), -1)
        cv2.rectangle(frame, (10, 10), (250, 80), (60, 60, 60), 1)

        # Display FPS and Tracked Objects Count
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
        cv2.putText(frame, f"Tracked Objects: {active_track_count}", (20, 68),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 200, 0), 2)

        # Display Frame
        cv2.imshow("Real-Time Object Detection & Tracking", frame)

        # 6. Keyboard Interactivity
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("[INFO] Exiting...")
            break
        elif key == ord('s'):
            filename = f"snapshot_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            print(f"[INFO] Snapshot saved to: {filename}")

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()