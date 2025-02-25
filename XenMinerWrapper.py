import os
import re
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime
import requests
import psutil
import tkinter as tk
from tkinter import messagebox, ttk

# Constants
DEFAULT_MINER_LOCATION = 'https://github.com/jacklevin74/xenminer/blob/main/miner.py'
DEFAULT_CONFIG_LOCATION = 'https://github.com/jacklevin74/xenminer/blob/main/config.conf'
ETH_ADDRESS_PATTERN = re.compile(r'^0x[0-9a-fA-F]{40}$')
HASH_PER_SECOND_PATTERN = re.compile(r',\s*([\d.]+)')
DIFFICULTY_PATTERN = re.compile(r"Updating difficulty to (\d+)")


class MinerApp(tk.Tk):
    def __init__(self):
        self.is_running = False
        super().__init__()

        # Initialize variables
        self.start_time = datetime.now()
        self.miner_hash_rates = {}
        self.valid_hash_count = 0
        self.lock = threading.Lock()
        self.current_difficulty = 0  # Initialize to a default value

        # GUI setup
        self.title("Xen Block Miner")
        self.geometry("1028x768")
        self.setup_ui()
        self.running_processes = []
        self.update_total_hash_rate()



    def setup_ui(self):

        self.footer_frame = self.create_footer_frame()
        self.create_links_in_footer()
        self.eth_address = self.create_label_and_entry("你的ETH钱包地址", 1, self.load_eth_address())
        self.python_env = self.create_label_and_entry("Python 环境路径", 2, self.load_python_env())
        self.create_label_and_combobox("并发数", 3)
        self.button_frame = tk.Frame(self)
        self.button_frame.grid(row=4, column=0, columnspan=2, pady=5)
        self.run_btn = tk.Button(self.button_frame, text="运行", command=self.run_script,
                                 background='green', foreground='grey', font=("Arial", 12, "bold"))
        self.run_btn.grid(row=4, column=0, padx=5)
        self.stop_btn = tk.Button(self.button_frame, text="停止", command=self.stop_script,
                                  state=tk.DISABLED, background='light grey', foreground='grey', font=("Arial", 12, "bold"))
        self.stop_btn.grid(row=4, column=1, padx=5)
        self.tab_control = ttk.Notebook(self)
        self.tab_control.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.footer_frame.grid(row=7, column=0, columnspan=2)

        self.python_env_label = tk.Label(self, text="Python 环境路径")
        self.python_env_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        self.python_paths = self.find_python_paths()
        self.python_env = ttk.Combobox(self, values=self.python_paths, width=70)
        self.python_env.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.python_env.insert(0, self.load_python_env())

    def update_python_env_from_combobox(self, event):
        selected_path = self.python_path_combobox.get()
        self.python_env.delete(0, tk.END)
        self.python_env.insert(0, selected_path)

    def create_label_and_entry(self, label_text, row, default_value=""):
            tk.Label(self, text=label_text).grid(row=row, column=0, padx=10, pady=10, sticky="e")
            entry = tk.Entry(self, width=70)
            entry.grid(row=row, column=1, padx=10, pady=10, sticky="w")
            entry.insert(0, default_value)
            return entry

    def create_label_and_combobox(self, label_text, row):
        tk.Label(self, text=label_text).grid(row=row, column=0, padx=10, pady=10, sticky="e")
        max_parallel = psutil.cpu_count(logical=False)
        values = [str(i) for i in range(1, max_parallel + 1)]
        self.num_parallel = ttk.Combobox(self, values=values)  # Assign to self.num_parallel
        self.num_parallel.set("1")
        self.num_parallel.grid(row=row, column=1, padx=10, pady=10, sticky="w")

    def toggle_run_button(self, state):
        if state == "disabled":
            self.run_btn.config(state=tk.DISABLED, background='light grey')
            self.stop_btn.config(state=tk.NORMAL, background='orange')
            self.num_parallel.config(state=tk.DISABLED)
        else:
            self.run_btn.config(state=tk.NORMAL, background='green')
            self.stop_btn.config(state=tk.NORMAL, background='light grey')
            self.num_parallel.config(state=tk.NORMAL)

    def toggle_stop_button(self, state):
        if state == "disabled":
            self.stop_btn.config(state=tk.DISABLED, background='light grey')
            self.run_btn.config(state=tk.NORMAL, background='green')
            self.num_parallel.config(state=tk.NORMAL)
        else:
            self.stop_btn.config(state=tk.NORMAL, background='orange')
            self.run_btn.config(state=tk.DISABLED, background='light grey')
            self.num_parallel.config(state=tk.DISABLED)


    def run_script(self):
        self.save_python_env()
        self.save_eth_address()
        self.is_running = True
        self.toggle_run_button("disabled")
        self.stop_btn.config(state=tk.NORMAL)
        python_env = self.python_env.get().strip()
        eth_address = self.eth_address.get().strip()


        if not self.validate_ethereum_address(eth_address):
            messagebox.showerror("Error", "Invalid Ethereum Address!")
            self.toggle_run_button("normal")  # Enable the "Run" button
            return

        if not python_env:
            messagebox.showerror("Error", "Please specify the path to Python Environment! (e.g. C:\python\python.exe)")
            self.toggle_run_button("normal")  # Enable the "Run" button
            return



        # Update the URLs to point to the raw GitHub content
        miner_location = DEFAULT_MINER_LOCATION.replace("github.com", "raw.githubusercontent.com").replace("/blob", "")
        config_location = DEFAULT_CONFIG_LOCATION.replace("github.com", "raw.githubusercontent.com").replace("/blob", "")

        try:
            # Download miner.py
            miner_script = requests.get(miner_location).text
            with open("miner.py", "w") as f:
                f.write(miner_script)
            config_content = requests.get(config_location).text  # Changed variable name here
            with open("config.conf", "w") as f:
                f.write(config_content)  # Now writing config_content to config.conf
        except:
            messagebox.showerror("Error", "Failed to fetch the scripts!")
            return

        time.sleep(1)


        with open("config.conf", "r") as file:
            lines = file.readlines()

        with open("config.conf", "w") as file:
            for line in lines:
                if line.strip().startswith("account ="):
                    file.write(f'account = {eth_address}\n')
                else:
                    file.write(line)

        with open("config.conf", "r") as f:
            updated_config_content = f.read()


        process = subprocess.Popen([python_env, 'miner.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        with self.lock:
            self.running_processes.append(process)

        try:
            miner_script = requests.get(miner_location).text
        except:
            messagebox.showerror("Error", "Failed to fetch the miner script!")
            return


        for tab in self.tab_control.tabs():
            self.tab_control.forget(tab)

        self.add_new_tab(updated_config_content, eth_address)
        for i in range(int(self.num_parallel.get())):
            tab = ttk.Frame(self.tab_control)
            self.tab_control.add(tab, text=f"Miner #{i+1}")

            v_scroll = tk.Scrollbar(tab, orient="vertical")
            v_scroll.grid(row=0, column=1, sticky="ns")

            output_display = tk.Text(tab, wrap=tk.WORD, yscrollcommand=v_scroll.set)
            output_display.grid(row=0, column=0, sticky="nsew")

            v_scroll.config(command=output_display.yview)

            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)
            self.run_miner_script(output_display, i)






    def run_miner_script(self, output_widget, miner_number):
        python_env = self.python_env.get().strip()
        def get_hash_per_second(line):
            # Using regex to find the first number after the first comma.
            match = re.search(r',\s*([\d.]+)', line)

            if match:
                return float(match.group(1))
            else:
                return None
        def extract_difficulty(line):
            match = re.search(r"Updating difficulty to (\d+)", line)
            if match:
                return int(match.group(1))
            return None


        def run():
            process = subprocess.Popen(
                [python_env, 'miner.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            with self.lock:
                self.running_processes.append(process)

            while True:
                line = process.stdout.readline()
                if not line:
                    break

                if "HTTP Status Code: 200" in line:
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.last_found_block_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"Detected a valid hash (mined a new block) at {current_time}!")

                    with self.lock:
                        self.valid_hash_count += 1
                    continue
                hash_per_second = get_hash_per_second(line)
                if hash_per_second:
                    self.miner_hash_rates[miner_number] = hash_per_second
                    output_widget.insert(tk.END, f"Hash Rate: {hash_per_second}\n")
                    output_widget.yview(tk.END)  # Auto-scroll to the bottom
                else:
                    output_widget.insert(tk.END, line)
                    output_widget.yview(tk.END)  # Auto-scroll to the bottom


                difficulty_update = extract_difficulty(line)
                if difficulty_update is not None:
                    self.current_difficulty = difficulty_update

            process.wait()

        threading.Thread(target=run, daemon=True).start()

    def reset_footer_labels(self):
        self.footer_blocks_var.set("出块数: --")
        self.footer_hash_rate_var.set("总算力 Hash/s: --")
        self.footer_latest_found_var.set("最后出块: --")
        self.footer_difficulty_var.set("难度: --")
        self.footer_blocks_per_day_var.set("Est. Blocks/Day: --")
        self.footer_elapsed_time_var.set("运行时间: --")

    def update_total_hash_rate(self):
        self.footer_blocks_var.set(f"出块数: {self.valid_hash_count:,}")
        total_hash_rate = sum(self.miner_hash_rates.values())
        self.footer_hash_rate_var.set(f"算力 Hash/s: {total_hash_rate:,.2f}")
        elapsed_time_in_seconds = (datetime.now() - self.start_time).total_seconds()
        if elapsed_time_in_seconds != 0:
            blocks_per_day = (self.valid_hash_count / elapsed_time_in_seconds) * 86400
        else:
            blocks_per_day = 0

        if hasattr(self, 'last_found_block_time'):
            self.footer_latest_found_var.set(f"最后出块: {self.last_found_block_time}")

        if isinstance(self.current_difficulty, (int, float)):
            self.footer_difficulty_var.set(f"难度: {self.current_difficulty:,}")
        else:
            self.footer_difficulty_var.set(f"难度: {self.current_difficulty}")

        self.footer_elapsed_time_var.set(f"运行时间: {self.get_elapsed_time()}")
        self.footer_blocks_per_day_var.set(f"Est. Blocks/Day: {blocks_per_day:.6f}")

        self.after(1000, self.update_total_hash_rate)

    def get_elapsed_time(self):
        delta = datetime.now() - self.start_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}d {hours:02}:{minutes:02}:{seconds:02}"

    def open_webpage(self, url):
        webbrowser.open(url)

    def load_python_env(self):
        if os.path.exists('python_env.txt'):
            with open('python_env.txt', 'r') as f:
                return f.read().strip()
        return ""

    def save_python_env(self):
        with open('python_env.txt', 'w') as f:
            f.write(self.python_env.get())

    def load_eth_address(self):
        if os.path.exists('eth_address.txt'):
            with open('eth_address.txt', 'r') as f:
                return f.read().strip()
        return ""

    def save_eth_address(self):
        with open('eth_address.txt', 'w') as f:
            f.write(self.eth_address.get())

    def validate_ethereum_address(self, address):
        return ETH_ADDRESS_PATTERN.match(address)

    def add_new_tab(self, content, eth_address):
        tab = ttk.Frame(self.tab_control)
        self.tab_control.add(tab, text="Config.conf", sticky="nsew")

        download_time = datetime.now().strftime("%a %b %d %Y at %I:%M:%S %p")
        download_info = f"Last download: {download_time}\nOriginal Github Ethereum address has been replaced by your own: {eth_address}\n\n"

        v_scroll = tk.Scrollbar(tab, orient="vertical")
        v_scroll.grid(row=0, column=1, sticky="ns")

        script_display = tk.Text(tab, wrap=tk.WORD, yscrollcommand=v_scroll.set, font=("Arial", 10))
        script_display.tag_configure("download_info", foreground="blue", font=("Arial", 10, "bold"))
        script_display.insert(tk.END, download_info, "download_info")  # Apply the "download_info" tag to this content
        script_display.insert(tk.END, content)
        script_display.grid(row=0, column=0, sticky="nsew")

        v_scroll.config(command=script_display.yview)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        self.tab_control.select(tab)
    def stop_script(self):
        with self.lock:
            for process in self.running_processes:
                try:
                    process.terminate()
                except Exception as e:
                    print(f"Error stopping process: {e}")

        self.running_processes.clear()

        for tab in self.tab_control.tabs():
            self.tab_control.forget(tab)
        self.run_btn.config(state=tk.NORMAL)
        self.toggle_stop_button("disabled")
        self.current_difficulty = 0
        time.sleep(1)
        self.reset_footer_labels()
        self.update_idletasks()  # Force the GUI to update immediately




    def on_closing(self):
        self.reset_footer_labels()
        self.stop_script()
        self.destroy()

    def create_footer_frame(self):
        footer_frame = ttk.Frame(self)
        self.footer_blocks_var = tk.StringVar(value="出块数: --")
        self.footer_hash_rate_var = tk.StringVar(value="总算力 Hash/s: --")
        self.footer_latest_found_var = tk.StringVar(value="最后出块: 0")
        self.footer_difficulty_var = tk.StringVar(value=f"难度: {self.current_difficulty}")
        self.footer_elapsed_time_var = tk.StringVar(value="运行时间: --")
        self.footer_blocks_per_day_var = tk.StringVar(value="Est. Blocks/Day: --")


        footer_blocks_label = ttk.Label(footer_frame, textvariable=self.footer_blocks_var)
        footer_hash_rate_label = ttk.Label(footer_frame, textvariable=self.footer_hash_rate_var)
        footer_latest_found_label = ttk.Label(footer_frame, textvariable=self.footer_latest_found_var)
        footer_difficulty_label = ttk.Label(footer_frame, textvariable=self.footer_difficulty_var)
        footer_elapsed_time_label = ttk.Label(footer_frame, textvariable=self.footer_elapsed_time_var)
        footer_blocks_per_day_label = ttk.Label(footer_frame, textvariable=self.footer_blocks_per_day_var)

        footer_difficulty_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        footer_hash_rate_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        footer_blocks_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        footer_latest_found_label.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        footer_elapsed_time_label.grid(row=0, column=4, padx=5, pady=5, sticky="w")
        footer_blocks_per_day_label.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        return footer_frame

    def create_links_in_footer(self):
        link1 = tk.Label(self.footer_frame, text=" ", fg="blue", cursor="hand2")
        # link1.bind("<Button-1>", lambda e: self.open_webpage("https://github.com/jacklevin74/xenminer"))
        link1.grid(row=1, column=2, sticky='w')

        # link2 = tk.Label(self.footer_frame, text="XM Wrapper", fg="blue", cursor="hand2")
        # link2.bind("<Button-1>", lambda e: self.open_webpage("https://github.com/JozefJarosciak/XenMinerWrapper/"))
        # link2.grid(row=1, column=3, sticky='w')

        # link3 = tk.Label(self.footer_frame, text="XenBlocks Dashboard", fg="blue", cursor="hand2")
        # link3.bind("<Button-1>", lambda e: self.open_webpage("https://xen.pub/index-xenblocks.php"))
        # link3.grid(row=1, column=4, sticky='w')

    def find_python_paths(self):
        python_paths = set()

        # Check common locations
        if sys.platform == 'win32':
            for common_location in ["C:\\Python{0}{1}\\python.exe".format(i, j) for i in range(3, 10) for j in range(0, 10)]:
                if os.path.exists(common_location):
                    python_paths.add(common_location)
        elif sys.platform == 'darwin':  # macOS
            common_locations = [
                "/usr/local/bin/python3",
                "/usr/bin/python3",
            ]
            python_paths.update(filter(os.path.exists, common_locations))
        else:  # Linux and other UNIX-like systems
            try:
                result = subprocess.run(['whereis', '-b', 'python'], stdout=subprocess.PIPE, text=True)
                paths = result.stdout.split()
                python_paths.update(path for path in paths[1:] if path.endswith('python3') or path.endswith('python'))
            except Exception as e:
                print(f"Error running whereis command: {e}")

        # Check PATH environment variable
        for path_dir in os.environ['PATH'].split(os.pathsep):
            python_path = os.path.join(path_dir, 'python.exe' if sys.platform == 'win32' else 'python3')
            if os.path.exists(python_path):
                python_paths.add(python_path)

        # Use shutil.which to find python executable
        which_python = shutil.which('python3') or shutil.which('python')
        if which_python:
            python_paths.add(which_python)

        return list(python_paths)


if __name__ == "__main__":
    app = MinerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
