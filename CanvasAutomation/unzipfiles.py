import os
import zipfile

def unzip_all(path):
    for filename in os.listdir(path):
        if filename.endswith(".zip"):
            zip_path = os.path.join(path, filename)
            extract_folder = os.path.join(path, os.path.splitext(filename)[0])

            if not os.path.exists(extract_folder):
                os.makedirs(extract_folder)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)
            print(f"Extracted: {filename} to {extract_folder}")


def delete_zip_files(folder_path):
   for filename in os.listdir(folder_path):
        if filename.endswith('.zip'):
            file_path = os.path.join(folder_path, filename)
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")


folder_path = 'C:/Workspace/Rutgers/Sem3/CS142_Data101_Sem3/Spring 2025/Assessments/HW1/Section 7'


#unzip_all(folder_path)

delete_zip_files(folder_path)