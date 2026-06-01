import cv2
import json
import os

VIDEO_PATH = 'test_video.mp4'

if not os.path.exists(VIDEO_PATH):
    print(f"❌ الفيديو مش موجود في الفولدر! اتأكد إن اسمه {VIDEO_PATH}")
    exit()

cap = cv2.VideoCapture(VIDEO_PATH)
success, frame = cap.read()
if not success:
    print("❌ مش قادر أقرأ أول فريم من الفيديو.")
    exit()

zones = {}
# أسماء الموظفين اللي في التجربة بتاعتنا
employee_names = ['hamdy', 'mayar', 'azza', 'mohamed', 'aya']

print("--- ابدأ تحديد المكاتب بالماوس ---")
print("1. ارسم مربع بالماوس حول مكتب الموظف.")
print("2. اضغط ENTER لتأكيد المربع.")
print("---------------------------------")

for name in employee_names:
    # نافذة اختيار المنطقة (ROI)
    roi = cv2.selectROI(f"Select Desk for: {name}", frame, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()
    
    x, y, w, h = roi
    # لو قفلت النافذة من غير ما ترسم، هيعتبرك لغيت الموظف ده
    if w == 0 or h == 0:
        print(f"⚠️ تم تخطي مكتب {name}")
        continue
        
    # حفظ الإحداثيات 
    zones[name] = [x, y, x + w, y + h]
    print(f"✅ تم حفظ مكتب {name}")

# حفظ الملف في json
with open('zones.json', 'w', encoding='utf-8') as f:
    json.dump(zones, f, ensure_ascii=False, indent=4)

print("\n🎉 ممتاز! تم إنشاء ملف zones.json بنجاح وفيه كل المكاتب.")
cap.release()