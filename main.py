import os
import qrcode
from qrcode.constants import ERROR_CORRECT_M, ERROR_CORRECT_Q
import cv2 as cv
import tkinter as tk
from tkinter import messagebox, filedialog
from pyzbar.pyzbar import decode


# ===============================
# Root Window
# ===============================
root = tk.Tk()
root.title("QR Tool")
root.resizable(False, False)

# ===============================
# Utility: Detect QR From Image
# ===============================
def detect_qr_from_gray(gray):
    detector = cv.QRCodeDetector()

    # First attempt
    data, points, _ = detector.detectAndDecode(gray)
    if data:
        return data

    # Second attempt (resized)
    gray2 = cv.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv.INTER_LINEAR)
    data2, points2, _ = detector.detectAndDecode(gray2)
    return data2


# ===============================
# QR Generator Section
# ===============================
gen_frame = tk.LabelFrame(root, text="QR Code Generator", padx=10, pady=10)
gen_frame.pack(fill="x", padx=10, pady=5)

tk.Label(gen_frame, text="Text / Link:").grid(row=0, column=0, sticky="e")
tk.Label(gen_frame, text="Output Filename:").grid(row=1, column=0, sticky="e")

text_entry = tk.Entry(gen_frame, width=50)
text_entry.grid(row=0, column=1, padx=5, pady=5)

output_entry = tk.Entry(gen_frame, width=50)
output_entry.grid(row=1, column=1, padx=5, pady=5)


def generate_qr():
    data = text_entry.get().strip()
    filename = output_entry.get().strip()

    if not data:
        messagebox.showerror("Error", "Text/Link cannot be empty")
        return

    if not filename or filename == ".png":
        filename = "qr.png"

    if not filename.lower().endswith(".png"):
        filename += ".png"

    output_dir = "data/output"
    os.makedirs(output_dir, exist_ok=True)

    full_path = os.path.join(output_dir, filename)

    ec_level = ERROR_CORRECT_Q if len(data) > 200 else ERROR_CORRECT_M
    box_size = 18 if len(data) > 200 else 12

    try:
        qr = qrcode.QRCode(
            error_correction=ec_level,
            box_size=box_size,
            border=4
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(full_path)

        messagebox.showinfo("Success", f"Saved to:\n{full_path}")

    except Exception as e:
        messagebox.showerror("Error", str(e))


tk.Button(gen_frame, text="Generate", command=generate_qr)\
    .grid(row=2, column=1, sticky="w")


# ===============================
# Image Scanner Section
# ===============================
scan_img_frame = tk.LabelFrame(root, text="QR Image Scanner", padx=10, pady=10)
scan_img_frame.pack(fill="x", padx=10, pady=5)

tk.Label(scan_img_frame, text="Select Image:").grid(row=0, column=0, sticky="w")

image_path_entry = tk.Entry(scan_img_frame, width=40)
image_path_entry.grid(row=0, column=1, padx=5)

result_text = tk.Text(scan_img_frame, height=3, width=50)
result_text.grid(row=2, column=0, columnspan=4, padx=5, pady=5)


def browse_image():
    path = filedialog.askopenfilename(
        title="Select QR Image",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
    )
    if path:
        image_path_entry.delete(0, tk.END)
        image_path_entry.insert(0, path)


def scan_image():
    path = image_path_entry.get().strip().strip('"').strip("'")

    if not path:
        messagebox.showerror("Error", "Path cannot be empty")
        return

    if not os.path.exists(path):
        messagebox.showerror("Error", "File not found")
        return

    img = cv.imread(path)
    if img is None:
        messagebox.showerror("Error", "Could not read image")
        return

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    data = detect_qr_from_gray(gray)

    result_text.delete("1.0", tk.END)

    if data:
        result_text.insert(tk.END, data)
        image_path_entry.delete(0, tk.END)
    else:
        result_text.insert(tk.END, "No QR Found")


tk.Button(scan_img_frame, text="Browse", command=browse_image)\
    .grid(row=0, column=2, padx=5)

tk.Button(scan_img_frame, text="Scan", command=scan_image)\
    .grid(row=0, column=3, padx=5)

tk.Label(scan_img_frame, text="Result:")\
    .grid(row=1, column=0, pady=5, sticky="w")


# ===============================
# Camera Scanner Section
# ===============================
scan_cam_frame = tk.LabelFrame(root, text="QR Camera Scanner", padx=10, pady=10)
scan_cam_frame.pack(fill="x", padx=10, pady=5)

camera_result_text = tk.Text(scan_cam_frame, height=3, width=50)
camera_result_text.grid(row=2, column=0, padx=5, pady=4)


def scan_camera():
    cap = cv.VideoCapture(0)

    if not cap.isOpened():
        messagebox.showerror("Error", "Camera not accessible")
        return None

    detected_data = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        codes = decode(frame)

        for code in codes:
            detected_data = code.data.decode("utf-8")
            x, y, w, h = code.rect
            cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv.imshow("QR Scanner", frame)

        if detected_data is not None:
            cv.waitKey(500)
            camera_result_text.insert(tk.END, detected_data)
            break
        if cv.waitKey(1) & 0xFF == 27:  # ESC key
            break

    cap.release()
    cv.destroyAllWindows()
tk.Button(scan_cam_frame, text="Camera Scan", command=scan_camera)\
    .grid(row=0, column=0, pady= 3, sticky="w")
tk.Label(scan_cam_frame, text="Press ESC to close the camera:").grid(row=3, column=0, pady=5, sticky="w")

# ===============================
# Start App
# ===============================
root.mainloop()
