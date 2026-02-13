import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import cv2 as cv

from core.generate import generate_qr
from core.scan_image import decode_qr_from_image
from core.scan_camera import scan_camera_flow


class QRToolGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QR Tool - GUI")
        self.geometry("640x420")
        self.resizable(False, False)

        self.clipboard_menu = self._create_clipboard_menu()
        self._setup_clipboard_shortcuts()

        self._build_generate_section()
        self._build_scan_image_section()
        self._build_scan_camera_section()

    def _create_clipboard_menu(self):
        menu = tk.Menu(self, tearoff=False)
        menu.add_command(label="Cut", command=lambda: self._clipboard_event("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: self._clipboard_event("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: self._clipboard_event("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: self._clipboard_event("<<SelectAll>>"))
        return menu

    def _setup_clipboard_shortcuts(self):
        for event_name in ("<Control-c>", "<Control-C>", "<Control-v>", "<Control-V>", "<Control-x>", "<Control-X>", "<Control-a>", "<Control-A>"):
            self.bind_all(event_name, self._on_clipboard_shortcut, add="+")

    def _on_clipboard_shortcut(self, event):
        widget = self.focus_get()
        if not isinstance(widget, (tk.Entry, tk.Text)):
            return

        key = event.keysym.lower()
        if key == "c":
            widget.event_generate("<<Copy>>")
        elif key == "v":
            widget.event_generate("<<Paste>>")
        elif key == "x":
            widget.event_generate("<<Cut>>")
        elif key == "a":
            widget.event_generate("<<SelectAll>>")

        return "break"

    def _clipboard_event(self, virtual_event):
        widget = self.focus_get()
        if isinstance(widget, (tk.Entry, tk.Text)):
            widget.event_generate(virtual_event)

    def _show_clipboard_menu(self, event):
        self.focus_set()
        event.widget.focus_set()
        self.clipboard_menu.tk_popup(event.x_root, event.y_root)

    def _build_generate_section(self):
        frame = tk.LabelFrame(self, text="Generate QR", padx=10, pady=10)
        frame.pack(fill="x", padx=12, pady=(12, 8))

        tk.Label(frame, text="Text / Link:").grid(row=0, column=0, sticky="w")
        self.data_entry = tk.Entry(frame, width=60)
        self.data_entry.grid(row=0, column=1, padx=8, pady=4, sticky="w")
        self.data_entry.bind("<Button-3>", self._show_clipboard_menu)

        tk.Label(frame, text="Output filename:").grid(row=1, column=0, sticky="w")
        self.filename_entry = tk.Entry(frame, width=30)
        self.filename_entry.insert(0, "qr.png")
        self.filename_entry.grid(row=1, column=1, padx=8, pady=4, sticky="w")
        self.filename_entry.bind("<Button-3>", self._show_clipboard_menu)

        tk.Button(frame, text="Generate", command=self.on_generate).grid(
            row=2, column=1, pady=(8, 0), sticky="w"
        )

    def _build_scan_image_section(self):
        frame = tk.LabelFrame(self, text="Scan QR from Image", padx=10, pady=10)
        frame.pack(fill="x", padx=12, pady=8)

        self.image_path = tk.StringVar()
        image_entry = tk.Entry(frame, textvariable=self.image_path, width=52)
        image_entry.grid(
            row=0, column=0, padx=(0, 8), pady=4
        )
        image_entry.bind("<Button-3>", self._show_clipboard_menu)
        tk.Button(frame, text="Browse", command=self.browse_image).grid(row=0, column=1, pady=4)
        tk.Button(frame, text="Scan", command=self.on_scan_image).grid(row=0, column=2, padx=(8, 0), pady=4)

        tk.Label(frame, text="Result:").grid(row=1, column=0, sticky="nw", pady=(8, 0))
        self.scan_result = tk.Text(frame, width=62, height=4)
        self.scan_result.grid(row=2, column=0, columnspan=3, pady=(4, 0), sticky="w")
        self.scan_result.bind("<Button-3>", self._show_clipboard_menu)

    def _build_scan_camera_section(self):
        frame = tk.LabelFrame(self, text="Scan QR from Camera", padx=10, pady=10)
        frame.pack(fill="x", padx=12, pady=8)

        tk.Label(
            frame,
            text="Opens OpenCV camera window. Press 'q' in that window to stop.",
        ).pack(anchor="w")
        tk.Button(frame, text="Start Camera Scan", command=self.on_scan_camera).pack(
            anchor="w", pady=(8, 0)
        )

    def on_generate(self):
        data = self.data_entry.get().strip()
        if not data:
            messagebox.showerror("Error", "Text/Link cannot be empty.")
            return

        filename = self.filename_entry.get().strip().strip('"').strip("'")
        if not filename or filename == ".png":
            filename = "qr.png"
        if not filename.lower().endswith(".png"):
            filename += ".png"

        out_dir = "data/output"
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, filename)

        if os.path.exists(out_path):
            overwrite = messagebox.askyesno("Confirm", f"{filename} exists. Overwrite?")
            if not overwrite:
                return

        success, error = generate_qr(data, out_path)
        if success:
            normalized = out_path.replace("\\", "/")
            messagebox.showinfo("Success", f"Saved in {normalized}")
        else:
            messagebox.showerror("Error", f"Failed to save QR: {error}")

    def browse_image(self):
        path = filedialog.askopenfilename(
            title="Select image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp"), ("All files", "*.*")],
        )
        if path:
            self.image_path.set(path)

    def on_scan_image(self):
        path = self.image_path.get().strip().strip('"').strip("'")
        path = os.path.normpath(path)
        if not path:
            messagebox.showerror("Error", "Image path cannot be empty.")
            return
        if not os.path.exists(path):
            messagebox.showerror("Error", "File not found.")
            return

        image = cv.imread(path)
        if image is None:
            messagebox.showerror("Error", "Could not read image.")
            return

        data, _ = decode_qr_from_image(image)
        self.scan_result.delete("1.0", tk.END)
        if data is None:
            self.scan_result.insert(tk.END, "No QR found.")
        else:
            self.scan_result.insert(tk.END, data)

    def on_scan_camera(self):
        threading.Thread(target=scan_camera_flow, daemon=True).start()


if __name__ == "__main__":
    app = QRToolGUI()
    app.mainloop()
