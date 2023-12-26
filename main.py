import cv2
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import telegram


# Khai báo thông tin bot Telegram
bot_token = "6473041440:AAEvFul4-Wy0K144hR6dxRuPa3NPc0IUmzw"
chat_id = "6728680494"

bot = telegram.Bot(token=bot_token)


# Khởi tạo thư viện âm thanh
pygame.mixer.init()
alert_sound = pygame.mixer.Sound("beep-warning-6387.mp3") 
def play_alert_sound():
    alert_sound.play()
    
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
    if file_path:
        # Kiểm tra định dạng tệp
        if not file_path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.flv')):
            messagebox.showerror("Error", "Sai định dạng. Hãy chọn file khác")
            return
        cap = cv2.VideoCapture(file_path)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        ret, frame = cap.read()
        frame = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (25, 25), 0)
        last_frame = gray
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
            if cap.isOpened():
                ret, frame = cap.read()
                if not ret:  # Kiểm tra nếu không có khung hình trả về
                    messagebox.showinfo("Motion Detected", "Video đã kết thúc!")
                    break

                frame = cv2.resize(frame, (640, 480))
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (25, 25), 0)

                abs_img = cv2.absdiff(last_frame[y:y + h, x:x + w], gray[y:y + h, x:x + w])
                last_frame = gray


                _, img_mask = cv2.threshold(abs_img, 2, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(img_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    if cv2.contourArea(contour) < 900:
                        continue

                    x1, y1, w1, h1 = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x1 + x, y1 + y), (x1 + x + w1, y1 + y + h1), (0, 255, 0), 2)
                    cv2.putText(frame, 'Canh Bao', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                    # Kiểm tra thời gian từ lần chụp trước đó
                    current_time = datetime.now()
                    time_diff = (current_time - last_capture_time).total_seconds()
                    if time_diff >= 3:
                        # Chụp ảnh và lưu vào thư mục
                        last_capture_time = current_time
                        file_name = f"{output_dir}/motion_{current_time.strftime('%Y%m%d%H%M%S')}.jpg"
                        cv2.imwrite(file_name, frame)
                        # Phát âm thanh cảnh báo
                        play_alert_sound()

                        # Gửi ảnh qua bot Telegram
                        bot.sendPhoto(chat_id=chat_id, photo = open(file_name,"rb"), caption=" Nguy hiêm!")

                cv2.imshow("Motion Detection", frame)
                if cv2.waitKey(40) == 27:  # Nhấn Esc để thoát
                    break
        cap.release()
        cv2.destroyAllWindows()
def start_camera():
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
        print(ret)
        print(frame.shape)
        frame = cv2.resize(frame, (640, 480))

        # Lật lại cả khung hình
        frame = cv2.flip(frame, 1)
        # Lấy thời gian hiện tại
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%d/%m/%Y")

        # Hiển thị thời gian lên video
        cv2.putText(frame,current_time, (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame,current_date, (15, 55), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (25, 25), 0)

        abs_img = cv2.absdiff(last_frame[y:y + h, x:x + w], gray[y:y + h, x:x + w])
        last_frame = gray

        _, img_mask = cv2.threshold(abs_img, 10, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(img_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) < 900:
                continue

            x1, y1, w1, h1 = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x1 + x, y1 + y), (x1 + x + w1, y1 + y + h1), (0, 255, 0), 2)
            cv2.putText(frame, 'Canh Bao', (15, 85), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            # Kiểm tra thời gian từ lần chụp trước đó
            current_time = datetime.now()
            time_diff = (current_time - last_capture_time).total_seconds()
            if time_diff >= 3:
                # Chụp ảnh và lưu vào thư mục
                last_capture_time = current_time
                file_name = f"{output_dir}/motion_{current_time.strftime('%Y%m%d%H%M%S')}.jpg"
                cv2.imwrite(file_name, frame)
                # Phát âm thanh cảnh báo
                play_alert_sound()

                # Gửi ảnh qua bot Telegram
                bot.sendPhoto(chat_id=chat_id, photo = open(file_name,"rb"), caption=" Nguy hiêm!")


        cv2.imshow("Motion Detection", frame)

        if cv2.waitKey(40) == 27:  # Nhấn Esc để thoát
            break
    cap.release()
    cv2.destroyAllWindows()
root = tk.Tk()
root.title("Motion Detection")


file_button = tk.Button(root, text="Select Video File", command=select_file)
file_button.pack()

camera_button = tk.Button(root, text="Start Camera", command=start_camera)
camera_button.pack()

root.mainloop()
