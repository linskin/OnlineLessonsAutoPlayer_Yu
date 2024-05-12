import tkinter as tk
from tkinter import messagebox

from auto import manage_threads


def add_url():
    url = url_entry.get()
    if url:
        course_urls.append(url)
        url_listbox.insert(tk.END, url)
        url_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Warning", "URL cannot be empty!")


def delete_url():
    selected_index = url_listbox.curselection()
    if selected_index:
        index = selected_index[0]
        course_urls.pop(index)
        url_listbox.delete(index)
    else:
        messagebox.showwarning("Warning", "Please select a URL to delete!")


def change_cookie():
    cookie = cookie_entry.get()
    if cookie:
        global COOKIE
        COOKIE = cookie
        messagebox.showinfo("Info", "Cookie updated successfully!")
    else:
        messagebox.showwarning("Warning", "Cookie cannot be empty!")


def change_max_workers():
    workers = int(max_workers_entry.get())
    if workers > 0:
        global max_workers
        max_workers = workers
        messagebox.showinfo("Info", "Max workers updated successfully!")
    else:
        messagebox.showwarning("Warning", "Max workers must be a positive integer!")


def toggle_headless():
    global headless
    headless = not headless
    if headless:
        messagebox.showinfo("Info", "Will working without windows now.")
    else:
        messagebox.showinfo("Info", "Will working with windows now.")



def run_manage():
    if course_urls:
        manage_threads(course_urls, COOKIE, headless, max_workers)
    else:
        messagebox.showwarning("Warning", "No course URLs added!")


def check_before_run():
    if not course_urls:
        messagebox.showwarning("Warning", "No course URLs added!")
    elif not COOKIE:
        messagebox.showwarning("Warning", "Cookie is empty!")
    else:
        messagebox.showinfo("Info", "Program is running, please do not close the window")
        run_manage()


course_urls = [
    "https://nwnu.yuketang.cn/pro/lms/9mmGBp8hbja/16444474/studycontent",
    "https://nwnu.yuketang.cn/pro/lms/9mmGBp8jBbc/16444472/studycontent",
    "https://nwnu.yuketang.cn/pro/lms/9mmGBp92fEk/16444475/studycontent",
    "https://nwnu.yuketang.cn/pro/lms/ACuTgbmSA6c/16444488/studycontent",
    "https://nwnu.yuketang.cn/pro/lms/9mmGBp8xU5W/16444473/studycontent",
    "https://nwnu.yuketang.cn/pro/lms/Adri46cNpNJ/16444433/studycontent"
]
COOKIE = 'n17vt928119qxhl94fdegoydn45x8osd'
max_workers = 3
headless = True


root = tk.Tk()
root.title("Course Manager")

# Add URL section
add_url_frame = tk.Frame(root)
add_url_frame.pack(pady=10)
tk.Label(add_url_frame, text="Add URL:").grid(row=0, column=0)
url_entry = tk.Entry(add_url_frame, width=50)
url_entry.grid(row=0, column=1)
add_button = tk.Button(add_url_frame, text="Add", command=add_url)
add_button.grid(row=0, column=2)

# URL list section
url_list_frame = tk.Frame(root)
url_list_frame.pack(pady=10)
tk.Label(url_list_frame, text="Course URLs:").pack()
url_listbox = tk.Listbox(url_list_frame, width=70, height=10)
url_listbox.pack()
for url in course_urls:
    url_listbox.insert(tk.END, url)
delete_button = tk.Button(url_list_frame, text="Delete", command=delete_url)
delete_button.pack()

# Change Cookie section
change_cookie_frame = tk.Frame(root)
change_cookie_frame.pack(pady=10)
tk.Label(change_cookie_frame, text="Change Cookie:").grid(row=0, column=0)
cookie_entry = tk.Entry(change_cookie_frame, width=50)
cookie_entry.grid(row=0, column=1)
change_cookie_button = tk.Button(change_cookie_frame, text="Change", command=change_cookie)
change_cookie_button.grid(row=0, column=2)

# Change Max Workers section
change_workers_frame = tk.Frame(root)
change_workers_frame.pack(pady=10)
tk.Label(change_workers_frame, text="Max Workers:").grid(row=0, column=0)
max_workers_entry = tk.Entry(change_workers_frame, width=5)
max_workers_entry.insert(tk.END, str(max_workers))
max_workers_entry.grid(row=0, column=1)
change_workers_button = tk.Button(change_workers_frame, text="Change", command=change_max_workers)
change_workers_button.grid(row=0, column=2)

# Toggle Headless section
headless_frame = tk.Frame(root)
headless_frame.pack(pady=10)
headless_button = tk.Button(headless_frame, text="Without Windows", command=toggle_headless)
headless_button.pack()

# Run Manage section
run_manage_frame = tk.Frame(root)
run_manage_frame.pack(pady=10)
run_manage_button = tk.Button(run_manage_frame, text="Run Auto Play", command=check_before_run)
run_manage_button.pack()

root.mainloop()