import cv2
import os
from datetime import datetime
import asyncio
from telegram import Bot
import numpy as np
import time

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

ret, frame = cap.read()
frame = cv2.resize(frame, (640, 480))
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (25, 25), 0)
last_frame = gray

# Select the region of interest
roi = cv2.selectROI('Video', frame, fromCenter=False, showCrosshair=True)
cv2.destroyWindow('Video')
x, y, w, h = int(roi[0]), int(roi[1]), int(roi[2]), int(roi[3])
frame = cv2.flip(frame, 1)
print(x, y, w, h)

async def send_telegram_message(image_path):
    my_token = "6473041440:AAEvFul4-Wy0K144hR6dxRuPa3NPc0IUmzw"
    # Create bot instance
    bot = Bot(token=my_token)

    # Send the image as a photo
    await bot.send_photo(chat_id=6728680494, photo=open(image_path, 'rb'), caption='Vl có xâm nhập kìa!!!')

async def capture_and_send_motion():
    global last_frame  # Declare last_frame as a global variable
    last_sent_time = time.time()

    while True:
        _, frame = cap.read()
        frame = cv2.resize(frame, (640, 480))
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

            # Capture an image when motion is detected
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = f"motion_{timestamp}.jpg"
            cv2.imwrite(image_path, frame)

            current_time = time.time()
            if current_time - last_sent_time >= 10:
                # Create a new event loop or use the default event loop
                loop = asyncio.get_event_loop() if asyncio.get_event_loop() else asyncio.new_event_loop()

                # Run the send_telegram_message coroutine
                await send_telegram_message(image_path)

                # Remove the image after sending
                os.remove(image_path)

                last_sent_time = current_time

        cv2.imshow("Motion Detection", frame)

        if cv2.waitKey(40) == 27:  # Press Esc to exit
            break

    # Remove the remaining image if it exists
    if os.path.exists(image_path):
        os.remove(image_path)

# Create a new event loop or use the default event loop
loop = asyncio.get_event_loop() if asyncio.get_event_loop() else asyncio.new_event_loop()

# Run the capture_and_send_motion coroutine as a task
task = loop.create_task(capture_and_send_motion())

# Run the event loop
try:
    loop.run_until_complete(task)
except KeyboardInterrupt:
    pass

cap.release()
cv2.destroyAllWindows()