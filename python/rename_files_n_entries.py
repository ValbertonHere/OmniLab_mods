import os
from zipfile import ZipFile
from time import sleep

STR4REPLACE = 'omnilab'
STR2REPLACE = 'valberton'

folderPath = input('Enter folder path\n> ')
print()

print('Processing files and folders...', end='')
# Переименовываем файлы и папки.
for root, subdirs, files in os.walk(folderPath):
    for file in files:
        if file.endswith('.xml'):
            file_abs_path = os.path.join(root, file)

            with open(file_abs_path) as f2r:
                fdata = f2r.read()
            
            with open(file_abs_path, 'w+') as f2w:
                f2w.write(fdata.replace(STR4REPLACE, STR2REPLACE))

    for dir in subdirs:
        folder_abs_path = os.path.join(root, dir)
        if STR4REPLACE in folder_abs_path:
            os.rename(folder_abs_path, folder_abs_path.replace(STR4REPLACE, STR2REPLACE))

print('Done!')
print("Waiting for OS's file system update...")
sleep(1)

print('Packing folders in .mtmod...', end='')
# Запаковываем это в mtmod.
for dir in os.listdir(folderPath):
    zip_file = ZipFile(os.path.join(folderPath, dir + '.mtmod'), 'w')
    root_folder = os.path.join(folderPath, dir)

    for root, subdirs, files in os.walk(root_folder):
        for file in files:
            zip_file.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(root_folder + '\\res', '..')))
print('Done!')