import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime
import platform

# Optional beep cross-platform
def beep():
    try:
        if platform.system() == "Windows":
            import winsound
            winsound.Beep(1000, 200)
        else:
            os.system('echo -n "\a"')
    except:
        pass

# Detects the first available webcam
def find_available_camera():
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cap.release()
            return i
    return None

def scan_qr_code(frame, log_results=False, log_file="scanned_qr.txt", seen=None):
    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(frame)
    scanned_data = []

    if points is not None and data:
        points = np.int32(points).reshape((-1, 1, 2))
        cv2.polylines(frame, [points], True, (0, 255, 0), 3)
        cv2.putText(frame, f'{data}', (int(points[0][0][0]), int(points[0][0][1]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

        if seen is not None and data in seen:
            return frame, []

        scanned_data.append((data, "QR Code"))
        if seen is not None:
            seen.add(data)

        if log_results:
            save_to_file(data, "QR Code", log_file)
            beep()

    return frame, scanned_data

def save_to_file(data, barcode_type, file_path):
    with open(file_path, 'a') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"{timestamp}, {data}, {barcode_type}\n")

def start_scanner():
    camera_index = find_available_camera()
    if camera_index is None:
        messagebox.showerror("Camera Error", "No webcam found on this system.")
        return

    cap = cv2.VideoCapture(camera_index)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"scanned_qrcodes_{timestamp}.txt"
    seen = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        scanned_frame, scanned_data = scan_qr_code(frame, log_results=True, log_file=log_file, seen=seen)
        cv2.imshow('QR Code Scanner', scanned_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    messagebox.showinfo("Scanner Closed", f"Scanned data saved to {log_file}")

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    if file_path:
        image = cv2.imread(file_path)
        if image is None:
            messagebox.showerror("Error", "Could not open the selected image.")
            return
        scanned_image, scanned_data = scan_qr_code(image)
        cv2.imshow('QR Code Scanner - Image', scanned_image)
        if scanned_data:
            save_option = messagebox.askyesno("Save Results", "Do you want to save the scanned results?")
            if save_option:
                save_results_to_file(scanned_data, file_path)
        else:
            messagebox.showinfo("No QR Code Found", "No QR code detected in the selected image.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def save_results_to_file(scanned_data, source_file):
    log_file = f"scanned_results_{os.path.basename(source_file)}.txt"
    with open(log_file, 'w') as f:
        for data, barcode_type in scanned_data:
            f.write(f"{data}, {barcode_type}\n")
    messagebox.showinfo("Results Saved", f"Scanned results saved to {log_file}")

def view_log_file():
    log_files = [f for f in os.listdir('.') if f.startswith("scanned_qrcodes_") and f.endswith(".txt")]
    if not log_files:
        messagebox.showwarning("No Logs", "No log files found. Start scanning to generate logs.")
        return

    log_window = tk.Toplevel(app)
    log_window.title("Scanned Logs")
    log_text = tk.Text(log_window, wrap='word', height=20, width=80)

    for file in sorted(log_files):
        log_text.insert('end', f"\n=== {file} ===\n")
        with open(file, 'r') as f:
            log_text.insert('end', f.read())

    log_text.config(state='disabled')
    log_text.pack(padx=10, pady=10)

# GUI Setup
app = tk.Tk()
app.title("QR Code Scanner")
app.geometry("400x300")

title_label = tk.Label(app, text="QR Code Scanner", font=("Helvetica", 16, 'bold'))
title_label.pack(pady=15)

start_button = tk.Button(app, text="Start Webcam Scanner", command=start_scanner, font=('Arial', 12), bg='green', fg='white')
start_button.pack(pady=10)

open_file_button = tk.Button(app, text="Select Image File", command=select_file, font=('Arial', 12), bg='blue', fg='white')
open_file_button.pack(pady=10)

view_log_button = tk.Button(app, text="View Scan Logs", command=view_log_file, font=('Arial', 12), bg='gray', fg='white')
view_log_button.pack(pady=10)

footer_label = tk.Label(app, text="Press 'q' to exit webcam scanner.", fg="darkred", font=('Arial', 10))
footer_label.pack(pady=15)

app.mainloop()
