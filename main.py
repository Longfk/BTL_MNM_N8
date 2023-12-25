import cv2
import os
from datetime import datetime

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

ret, frame = cap.read()
frame = cv2.resize(frame, (640, 480))
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (25, 25), 0)
last_frame = gray
frame = cv2.flip(frame, 1)
# Chọn vùng cần quan sát
roi = cv2.selectROI('Video', frame, fromCenter=False, showCrosshair=True)
cv2.destroyWindow('Video')
x, y, w, h = int(roi[0]), int(roi[1]), int(roi[2]), int(roi[3])

print(x, y, w, h)

# Tạo thư mục chứa ảnh được chụp
output_dir = "captured_images"
os.makedirs(output_dir, exist_ok=True)

# Biến thời gian để theo dõi thời gian đã trôi qua từ lần chụp trước đó
last_capture_time = datetime.now()

while True:
    _, frame = cap.read()
    frame = cv2.resize(frame, (640, 480))

    # Lật lại cả khung hình
    frame = cv2.flip(frame, 1)

    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (25, 25), 0)

    abs_img = cv2.absdiff(last_frame[y:y + h, x:x + w], gray[y:y + h, x:x + w])
    last_frame = gray

    _, img_mask = cv2.threshold(abs_img, 30, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(img_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 900:
            continue

        x1, y1, w1, h1 = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x1 + x, y1 + y), (x1 + x + w1, y1 + y + h1), (0, 255, 0), 2)
        cv2.putText(frame, 'Canh Bao', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        # Kiểm tra thời gian từ lần chụp trước đó
        current_time = datetime.now()
        time_diff = (current_time - last_capture_time).total_seconds()
        if time_diff >= 3:
            # Chụp ảnh và lưu vào thư mục
            last_capture_time = current_time
            file_name = f"{output_dir}/motion_{current_time.strftime('%Y%m%d%H%M%S')}.jpg"
            cv2.imwrite(file_name, frame)

    cv2.imshow("Motion Detection", frame)

    if cv2.waitKey(40) == 27:  # Nhấn Esc để thoát
        break

cap.release()
cv2.destroyAllWindows()
