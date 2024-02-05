import ctypes
import multiprocessing
import os
import shutil
import time
import rarfile
import zipfile

import PyPDF2

from constants import *


def exit_func(error_message):
    print(error_message)
    exit()


def check_data(func_pdf_file_path, func_unlock_mode):
    try:
        func_unlock_mode = pw_mode_transform[func_unlock_mode]
    except:
        exit_func("Wrong pw type.")

    try:
        func_file_type = func_pdf_file_path.rsplit(".")[1]
    except:
        exit_func("Wrong file type")

    return func_unlock_mode, func_file_type


def get_data():
    pdf_file_path = "my_file.pdf"  # input("File name:")
    unlock_mode = "nums"  # input("What characters the password contains: [nums, nums+alpha, alpha, everything] ")

    unlock_mode, file_type = check_data(pdf_file_path, unlock_mode)

    return pdf_file_path, unlock_mode, file_type


def open_pdf(my_pw_found, file_name, start, end):
    with open(file_name, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        if not pdf_reader.is_encrypted:
            exit_func("File does not have password")

        # TODO fix this
        for password in range(start, end):
            if pdf_reader.decrypt(str(password)):
                my_pw_found.value = True
                exit_func(f"Password is: {password}")

            if my_pw_found.value:
                break


def open_rar(my_pw_found, file_name, start, end):
    for password in range(start, end):
        try:
            with rarfile.RarFile(file_name) as file:
                file.extractall(pwd=password)
                my_pw_found.value = True
                exit_func(f"Password is: {password}")
        except:
            ...

        if my_pw_found.value:
            break


def open_zip(my_pw_found, file_name, start, end):
    for password in range(start, end):
        try:
            with zipfile.ZipFile(file_name, "r") as file:
                file.extractall(pwd=password)
                my_pw_found.value = True
                exit_func(f"Password is: {password}")
        except:
            ...

        if my_pw_found.value:
            break


def hehe():
    open_zip("da", "da", "da", "da")


if __name__ == "__main__":
    start_time = time.time()
    pdf_file_path, unlock_mode, file_type = get_data()

    num_cores = multiprocessing.cpu_count()
    if os.path.exists(FOLDER_NAME):
        shutil.rmtree(FOLDER_NAME)

    os.mkdir(FOLDER_NAME)

    file_names = []
    for i in range(num_cores):
        try:
            shutil.copy(pdf_file_path, f"./tmp/{i}_{pdf_file_path}")
            file_names.append(f"./tmp/{i}_{pdf_file_path}")
        except FileNotFoundError as e:
            exit_func(e)

    pw_found = multiprocessing.Value(ctypes.c_bool, False)

    processes = []
    max_num = 9999999999
    start = 900000

    while True:
        for i in range(num_cores):
            end = start + 1000
            if file_type == "pdf":
                processes.append(
                    multiprocessing.Process(
                        target=open_pdf, args=(pw_found, file_names[i], start, end)
                    )
                )
            elif file_type == "rar":
                processes.append(
                    multiprocessing.Process(
                        target=open_rar, args=(pw_found, file_names[i], start, end)
                    )
                )
            elif file_type == "zip":
                processes.append(
                    multiprocessing.Process(
                        target=open_zip, args=(pw_found, file_names[i], start, end)
                    )
                )

            start = end

        for process in processes:
            process.start()

        for process in processes:
            process.join()

            processes = []

        if pw_found.value:
            break

        print(start)

        if end > max_num:
            break

    shutil.rmtree(FOLDER_NAME)
    print(f"Opening time: {time.time() - start_time:.2f} seconds")
