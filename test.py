# import tkinter as tk
# from tkinter import filedialog
# from PIL import Image
# import torch
# import torchvision.models as models
# import torchvision.transforms as transforms
# import cv2
# import numpy as np
# import openpyxl
# import sys
# import os
# import tkinter.messagebox as tk1
# from pathlib import Path
#
# # Add tkdesigner to path
# sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# try:
#     from tkdesigner.designer import Designer
# except ModuleNotFoundError:
#     raise RuntimeError("Couldn't add tkdesigner to the PATH.")
#
#
# # Path to asset files for this GUI window.
# ASSETS_PATH = Path(__file__).resolve().parent / "assets"
#
# # Required in order to add data files to Windows executable
# path = getattr(sys, '_MEIPASS', os.getcwd())
# os.chdir(path)
#
# output_path = ""
#
# # Load the pre-trained ResNet101 model
# model = models.efficientnet_b7(weights = 'DEFAULT')
#
# # Set the model to evaluation mode
# model.eval()
#
# # Define the transformations to be applied to the input image
# transform = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.ToTensor(),
#     transforms.Normalize(mean=[0.485, 0.456, 0.406],
#                          std=[0.229, 0.224, 0.225])
# ])
#
# # Create the GUI window
# window = tk.Tk()
# logo = tk.PhotoImage(file=ASSETS_PATH / "iconbitmap.gif")
# window.call('wm', 'iconphoto', window._w, logo)
# window.title("Predict House area")
# window.geometry("862x519")
# window.configure(bg="#3A7FF6")
# canvas = tk.Canvas(
#     window, bg="#3A7FF6", height=519, width=862,
#     bd=0, highlightthickness=0, relief="ridge")
# canvas.place(x=0, y=0)
# canvas.create_rectangle(431, 0, 431 + 431, 0 + 519, fill="#FCFCFC", outline="")
#
# def open_folder():
#     global folder_path
#     # Open a dialog to select a folder
#     folder_path = filedialog.askdirectory()
#
#     # Get the parent folder name
#     parent_folder_name = os.path.basename(os.path.dirname(folder_path))
#
#     # Create a label to display the predicted area
#     result_label = tk.Label(window)
#     result_label.pack()
#
#     # Predict the house area for all images in the selected folder
#     predict_house_area(folder_path, result_label)
#
# def predict_house_area(folder_path, label):
#     # Initialize the sum of predicted areas
#     global total_area_sqm,predicted_area,folder_name,parent_folder_name,parent_folder_path
#     total_area_sqm = 0
#
#     # Get the folder name
#     folder_name = os.path.basename(folder_path)
#     parent_folder_path = os.path.dirname(folder_path)
#
#     # Create a list to store the predicted areas for each image
#     predicted_areas = []
#
#     # Loop over all the images in the directory
#     for image_file in os.listdir(folder_path):
#
#         # Load the input image
#         img = Image.open(os.path.join(folder_path, image_file))
#
#         # Check if the image is PNG and convert to JPEG if it is
#         if img.format == "PNG":
#             # Convert the image to RGB format
#             img = img.convert("RGB")
#
#         # Apply the transformations to the input image
#         img_transformed = transform(img)
#
#         # Add a batch dimension to the transformed image tensor
#         img_transformed_batch = torch.unsqueeze(img_transformed, 0)
#
#         # Use the pre-trained model to make a prediction on the input image
#         with torch.no_grad():
#             output = model(img_transformed_batch)
#
#         # Convert the output tensor to a probability distribution using softmax
#         softmax = torch.nn.Softmax(dim=1)
#         output_probs = softmax(output)
#
#         # Extract the predicted class (house square footage) from the output probabilities
#         predicted_class = torch.argmax(output_probs)
#
#         if predicted_class in [861,648, 594,894,799,896,454]:
#             # Convert to grayscale and apply adaptive thresholding
#             gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
#             gray = cv2.GaussianBlur(gray, (5, 5), 0)
#             mask = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)
#
#
#             # Apply Canny edge detection to the binary mask
#             edges = cv2.Canny(mask, 30, 100)
#
#             # Apply dilation to fill gaps in the contour
#             kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
#             dilated = cv2.dilate(edges, kernel, iterations=2)
#             eroded = cv2.erode(dilated, kernel, iterations=1)
#
#             # Find contours in binary mask
#             contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
#             # Find largest contour and calculate area
#             max_area = 0
#             for c in contours:
#                 area = cv2.contourArea(c)
#                 if area > max_area:
#                     max_area = area
#
#             # Convert pixel area to square meters
#             pixels_per_meter = 300  # adjust this value based on your image resolution and actual room dimensions
#             predicted_area_sqm = (max_area + 10)/2/ pixels_per_meter ** 2
#
#         else:
#             predicted_area_sqft = predicted_class.item()
#             predicted_area_sqm = predicted_area_sqft * 0.092903 / 4.2
#
#         # Add the predicted area to the sum
#         total_area_sqm += predicted_area_sqm
#
#         # Add the predicted area to the list of predicted areas
#         predicted_areas.append(predicted_area_sqm)
#
#         print(f"Predicted house square footage for {image_file}: {predicted_area_sqm:.2f} square meters, predicted class: {predicted_class}")
#
#     print(f"Sum of predicted house square footage: {total_area_sqm:.2f} square meters")
#
#     # Get the parent folder name
#     parent_folder_name = os.path.basename(os.path.dirname(folder_path))
#
#     text_box_bg = tk.PhotoImage(file=ASSETS_PATH / "TextBox_Bg.png")
#     # result_entry_img = canvas.create_image(650.5, 167.5, image=text_box_bg)
#     # Create a StringVar object and set its value to the text that you want to display in the Entry widget
#     result_text = tk.StringVar(value=f"Tổng diện tích dự đoán {folder_name}: {total_area_sqm:.2f} m2")
#     # Create the entry widget
#     result_entry = tk.Entry(window, textvariable=result_text, bd=0, bg="#F6F7F9", fg="#000716", highlightthickness=0)
#     result_entry.place(x=490.0, y=137 + 25, width=321.0, height=35)
#     result_entry.focus()
#
# def export_data():
#     # Get the parent folder name
#     parent_folder_name = os.path.basename(parent_folder_path)
#
#     # Replace with your code to get the predicted_area data
#     data = [parent_folder_name, folder_name, total_area_sqm]
#     headers = ['Mã BĐS', 'Mã phòng', 'Diện tích']
#     df = [headers, data]
#
#     # Get the selected folder path to save the file
#     folder_selected = filedialog.askdirectory()
#
#     # Check if the file already exists in the selected folder
#     file_path = os.path.join(folder_selected, 'predicted_area.xlsx')
#     if os.path.exists(file_path):
#         # If the file exists, open it and get the existing worksheet
#         workbook = openpyxl.load_workbook(file_path)
#         worksheet = workbook.active
#         start_row = worksheet.max_row + 1  # Append to the end of the existing data
#     else:
#         # If the file doesn't exist, create a new workbook and worksheet
#         workbook = openpyxl.Workbook()
#         worksheet = workbook.active
#         start_row = 1  # Write the headers at the beginning of the new file
#         worksheet.append(headers)  # Write the headers to the worksheet
#
#     # Append the new data to the worksheet
#     for row in df[1:]:
#         worksheet.append(row)
#
#     # Save the workbook to the file
#     workbook.save(file_path)
#     tk.messagebox.showinfo('Export Data', f'Data exported to {file_path}')
#
# text_box_bg = tk.PhotoImage(file=ASSETS_PATH / "TextBox_Bg.png")
#
# path_entry = tk.Entry(bd=0, bg="#F6F7F9", fg="#000716", highlightthickness=0)
# path_entry.place(x=490.0, y=299+25, width=321.0, height=35)
#
# path_picker_img = tk.PhotoImage(file = ASSETS_PATH / "path_picker.png")
# path_picker_button = tk.Button(
#     image = path_picker_img,
#     text = f'',
#     compound = 'center',
#     fg = 'white',
#     borderwidth = 0,
#     highlightthickness = 0,
#     command = open_folder,
#     relief = 'flat')
#
# path_picker_button.place(
#     x = 783, y = 319,
#     width = 24,
#     height = 22)
#
# canvas.create_text(
#     490.0, 315.5, text="Select folder",
#     fill="#515486", font=("Arial-BoldMT", int(13.0)), anchor="w")
# canvas.create_text(
#     646.5, 428.5, text="Predict",
#     fill="#FFFFFF", font=("Arial-BoldMT", int(13.0)))
# canvas.create_text(
#     573.5, 88.0, text="Chose folder to predict",
#     fill="#515486", font=("Arial-BoldMT", int(22.0)))
#
# title = tk.Label(
#     text="Welcome to House Predictor", bg="#3A7FF6",
#     fg="white",justify="left", font=("Arial-BoldMT", int(20.0)))
# title.place(x=20.0, y=120.0)
# canvas.create_rectangle(25, 160, 33 + 60, 160 + 5, fill="#FCFCFC", outline="")
#
# info_text = tk.Label(
#     text="House Area Predictor\n"
#     "1. Chọn folder muốn tính tổng diện tích\n"
#     "2. Lưu ý chỉ chọn những folder chứa ảnh\n"
#     "không được chọn thư mục không có ảnh,\n"
#
#     "3. Kết quả diện tích dự đoán, \n"
#     "sẽ xuất ra bên trái màn hình, \n"
#     "4.Chọn 'give to exel' để xuất ra file exel",
#     bg="#3A7FF6", fg="white", justify="left",
#     font=("Georgia", int(16.0)))
#
# info_text.place(x=20.0, y=200.0)
#
# button_img = tk.PhotoImage(file=ASSETS_PATH / "generate - Copy.png")
# button_data = tk.Button(
#     image=button_img, borderwidth=0, highlightthickness=0,
#     command=export_data, relief="flat")
# button_data.place(x=557, y=461, width=180, height=55)
#
# window.resizable(False, False)
# window.mainloop()
