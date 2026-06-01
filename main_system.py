import cv2
import json
from datetime import datetime
from ultralytics import YOLO
import db_manager

# تهيئة الداتا بيز
db_manager.init_db()

# قراءة المكاتب
try:
    with open('zones.json', 'r', encoding='utf-8') as f:
        zones = json.load(f)
except FileNotFoundError:
    print("❌ ملف zones.json مش موجود. رن سكريبت setup_zones.py الأول!")
    exit()

print("⏳ جاري تحميل موديل YOLO الضخم وتجهيز النظام...")
model = YOLO('yolov8l.pt')

VIDEO_PATH = 'test_video.mp4'
cap = cv2.VideoCapture(VIDEO_PATH)
fps = cap.get(cv2.CAP_PROP_FPS) or 24

stats = {emp: {"desk_frames": 0} for emp in zones.keys()}
frame_counter = 0

# قاموس ربط رقم التتبع باسم الموظف لمنع التداخل
id_to_name = {}

print("✅ النظام شغال ومستقر تماماً! (اضغط 'q' في أي وقت للإغلاق)")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame_counter += 1
    
    # تشغيل التتبع بأقوى إعدادات وصلنا لها
    results = model.track(frame, persist=True, classes=[0], tracker="bytetrack.yaml", conf=0.05, iou=0.4, verbose=False)
    
    # رسم المكاتب الثابتة
    for emp_name, coords in zones.items():
        x1, y1, x2, y2 = coords
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
        cv2.putText(frame, emp_name, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        track_ids = results[0].boxes.id.cpu().numpy()

        for box, track_id in zip(boxes, track_ids):
            bx1, by1, bx2, by2 = map(int, box)
            cx, cy = (bx1 + bx2) // 2, (by1 + by2) // 2
            track_id = int(track_id)

            # تسجيل الهوية لأول مرة بناءً على أول مكتب يقعد عليه
            if track_id not in id_to_name:
                for emp_name, coords in zones.items():
                    zx1, zy1, zx2, zy2 = coords
                    if zx1 <= cx <= zx2 and zy1 <= cy <= zy2:
                        id_to_name[track_id] = emp_name
                        break

            current_person = id_to_name.get(track_id, "Unknown")

            # رسم المربع والنقطة المركزية
            cv2.rectangle(frame, (bx1, by1), (bx2, by2), (255, 0, 0), 1)
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
            cv2.putText(frame, f"{current_person} (ID:{track_id})", (bx1, by1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # حساب وقت التواجد الفعلي
            if current_person != "Unknown":
                my_coords = zones.get(current_person)
                if my_coords:
                    zx1, zy1, zx2, zy2 = my_coords
                    if zx1 <= cx <= zx2 and zy1 <= cy <= zy2:
                        stats[current_person]["desk_frames"] += 1
                        cv2.putText(frame, "Working", (bx1, by1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # ترحيل البيانات للداتا بيز كل ثانيتين (50 فريم)
    if frame_counter % 50 == 0:
        db_payload = {}
        for emp, data in stats.items():
            inc_seconds = data["desk_frames"] / fps
            db_payload[emp] = {"desk_inc": inc_seconds, "focus_inc": inc_seconds}
        db_manager.update_db(db_payload)
        for emp in stats: stats[emp]["desk_frames"] = 0

    cv2.imshow("AI Office System - Windows Stable", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()