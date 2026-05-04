import tkinter as tk
from tkinter import ttk
import json
import random
import os
import time

DATA_FOLDER = "data"
PROGRESS_FILE = "progress.json"

FEEDBACK_DELAY = 900  # ms


# ------------------------
# DATA UTILS
# ------------------------

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return {}
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def update_progress(progress, word, correct):
    now = time.time()

    if word not in progress:
        progress[word] = {
            "correct": 0,
            "shown": 0,
            "first_seen": now,
            "last_seen": now
        }

    progress[word]["shown"] += 1
    progress[word]["last_seen"] = now

    if correct:
        progress[word]["correct"] += 1


def get_percent(progress, word):
    if word not in progress or progress[word]["shown"] == 0:
        return 0
    return progress[word]["correct"] / progress[word]["shown"]


def percent_to_color(p):
    r = int(255 * (1 - p))
    g = int(255 * p)
    return f"#{r:02x}{g:02x}40"


# ------------------------
# SORTING
# ------------------------

def sort_by_performance(progress):
    return sorted(progress.items(),
                  key=lambda x: x[1]["correct"] / x[1]["shown"] if x[1]["shown"] else 0)

def sort_by_shown(progress):
    return sorted(progress.items(), key=lambda x: x[1]["shown"], reverse=True)

def sort_by_last_seen(progress):
    return sorted(progress.items(), key=lambda x: x[1]["last_seen"], reverse=True)

def sort_by_first_seen(progress):
    return sorted(progress.items(), key=lambda x: x[1]["first_seen"])

def sort_alphabetical(progress):
    return sorted(progress.items(), key=lambda x: x[0])

def sort_by_priority(progress):
    def score(item):
        stats = item[1]
        if stats["shown"] == 0:
            return 0
        accuracy = stats["correct"] / stats["shown"]
        return accuracy * stats["shown"]
    return sorted(progress.items(), key=score)


# ------------------------
# APP
# ------------------------

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Arabic Word Quiz")
        self.root.geometry("720x520")
        self.root.configure(bg="#0f172a")

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("TButton", font=("Arial", 12), padding=6)
        self.style.configure("Title.TLabel",
                             font=("Arial", 22, "bold"),
                             foreground="white",
                             background="#0f172a")
        self.style.configure("Card.TLabel",
                             font=("Arial", 38, "bold"),
                             background="#0f172a",
                             foreground="white")

        self.progress = load_progress()

        self.cards = []
        self.index = 0
        self.score = 0

        # GAME NAV STATE
        self.game_path = DATA_FOLDER
        self.game_history = []

        # REVIEW NAV STATE
        self.review_path = DATA_FOLDER
        self.review_history = []

        self.sort_mode = tk.StringVar(value="performance")

        self.main_menu()

    # ------------------------
    # UTILS UI
    # ------------------------

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    # ------------------------
    # MENU
    # ------------------------

    def main_menu(self):
        self.clear()

        ttk.Label(self.root, text="Arabic Word Quiz", style="Title.TLabel").pack(pady=30)

        ttk.Button(self.root, text="▶ Gioca", command=self.game_menu).pack(pady=10)
        ttk.Button(self.root, text="🧠 Ripasso intelligente", command=self.review_menu).pack(pady=10)
        ttk.Button(self.root, text="📊 Dashboard", command=self.dashboard).pack(pady=10)

    # ------------------------
    # GAME — FILE BROWSER
    # ------------------------

    def game_menu(self):
        self.game_path = DATA_FOLDER
        self.game_history = []
        self.open_game_folder(self.game_path)

    def open_game_folder(self, path):
        self.clear()

        ttk.Label(self.root, text=path, style="Title.TLabel").pack(pady=10)

        if self.game_history:
            ttk.Button(
                self.root,
                text="← Indietro",
                command=self.go_back_game
            ).pack(pady=5)

        items = sorted(os.listdir(path))

        for item in items:
            full_path = os.path.join(path, item)

            if os.path.isdir(full_path):
                ttk.Button(
                    self.root,
                    text=f"📁 {item}",
                    command=lambda p=full_path: self.enter_game_folder(p)
                ).pack(pady=3)

            elif item.endswith(".json"):
                ttk.Button(
                    self.root,
                    text=f"📄 {item}",
                    command=lambda p=full_path: self.start_game(p)
                ).pack(pady=3)

        ttk.Button(self.root, text="← Menu", command=self.main_menu).pack(pady=10)

    def enter_game_folder(self, path):
        self.game_history.append(self.game_path)
        self.game_path = path
        self.open_game_folder(path)

    def go_back_game(self):
        self.game_path = self.game_history.pop()
        self.open_game_folder(self.game_path)

    def start_game(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            cards = json.load(f)

        self.cards = cards
        random.shuffle(self.cards)

        self.index = 0
        self.score = 0

        self.show_question()

    # ------------------------
    # REVIEW SYSTEM — FILE BROWSER
    # ------------------------

    def review_menu(self):
        self.review_path = DATA_FOLDER
        self.review_history = []
        self.open_review_folder(self.review_path)

    def open_review_folder(self, path):
        self.clear()

        ttk.Label(self.root, text=path, style="Title.TLabel").pack(pady=10)

        if self.review_history:
            ttk.Button(
                self.root,
                text="← Indietro",
                command=self.go_back_review
            ).pack(pady=5)

        items = sorted(os.listdir(path))

        for item in items:
            full_path = os.path.join(path, item)

            if os.path.isdir(full_path):
                ttk.Button(
                    self.root,
                    text=f"📁 {item}",
                    command=lambda p=full_path: self.enter_review_folder(p)
                ).pack(pady=3)

            elif item.endswith(".json"):
                ttk.Button(
                    self.root,
                    text=f"📄 {item}",
                    command=lambda p=full_path: self.start_review(p)
                ).pack(pady=3)

        ttk.Button(self.root, text="← Menu", command=self.main_menu).pack(pady=10)

    def enter_review_folder(self, path):
        self.review_history.append(self.review_path)
        self.review_path = path
        self.open_review_folder(path)

    def go_back_review(self):
        self.review_path = self.review_history.pop()
        self.open_review_folder(self.review_path)

    # ------------------------
    # REVIEW START
    # ------------------------

    def start_review(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            cards = json.load(f)

        self.cards = cards  # qui puoi inserire filtro intelligente se vuoi

        random.shuffle(self.cards)

        self.index = 0
        self.score = 0

        self.show_question()

    # ------------------------
    # QUIZ CORE
    # ------------------------

    def show_question(self):
        self.clear()

        if self.index >= len(self.cards):
            self.show_result()
            return

        card = self.cards[self.index]

        ttk.Label(self.root, text=card["arabic"], style="Card.TLabel").pack(pady=40)

        self.feedback_label = tk.Label(self.root, text="", font=("Arial", 16), bg="#0f172a")
        self.feedback_label.pack(pady=10)

        for opt in card["options"]:
            ttk.Button(
                self.root,
                text=opt,
                command=lambda o=opt: self.check_answer(o)
            ).pack(pady=5)

        ttk.Button(self.root, text="← Menu", command=self.main_menu).pack(pady=15)

    def check_answer(self, selected):
        card = self.cards[self.index]
        correct = selected == card["correct"]

        update_progress(self.progress, card["arabic"], correct)

        if correct:
            self.score += 1
            self.feedback_label.config(text="✔ Corretto", fg="#22c55e")
        else:
            self.feedback_label.config(
                text=f"✘ Sbagliato (giusto: {card['correct']})",
                fg="#ef4444"
            )

        self.index += 1
        self.root.after(FEEDBACK_DELAY, self.show_question)

    def show_result(self):
        save_progress(self.progress)
        self.clear()

        total = len(self.cards)
        percent = (self.score / total) * 100 if total else 0

        ttk.Label(self.root, text="Risultato", style="Title.TLabel").pack(pady=20)
        ttk.Label(self.root, text=f"{self.score}/{total}", font=("Arial", 18)).pack(pady=5)
        ttk.Label(self.root, text=f"{percent:.1f}%", font=("Arial", 18)).pack(pady=5)

        ttk.Button(self.root, text="Menu", command=self.main_menu).pack(pady=20)

    # ------------------------
    # DASHBOARD
    # ------------------------

    def dashboard(self):
        self.clear()

        ttk.Label(self.root, text="Dashboard", style="Title.TLabel").pack(pady=10)

        # Sorting controls
        sort_frame = tk.Frame(self.root, bg="#0f172a")
        sort_frame.pack(pady=5)

        sorts = [
            ("Performance", "performance"),
            ("Viste", "shown"),
            ("Recenti", "recent"),
            ("Prime viste", "first"),
            ("A-Z", "alpha"),
            ("Priorità", "priority"),
        ]

        for label, mode in sorts:
            tk.Radiobutton(
                sort_frame,
                text=label,
                variable=self.sort_mode,
                value=mode,
                command=self.dashboard,
                bg="#0f172a",
                fg="white",
                selectcolor="#1e293b",
                activebackground="#0f172a",
                activeforeground="white"
            ).pack(side="left", padx=4)

        # Scrollable word list
        container = tk.Frame(self.root, bg="#0f172a")
        container.pack(fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(container, bg="#0f172a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#0f172a")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        mode = self.sort_mode.get()
        if mode == "performance":
            items = sort_by_performance(self.progress)
        elif mode == "shown":
            items = sort_by_shown(self.progress)
        elif mode == "recent":
            items = sort_by_last_seen(self.progress)
        elif mode == "first":
            items = sort_by_first_seen(self.progress)
        elif mode == "alpha":
            items = sort_alphabetical(self.progress)
        elif mode == "priority":
            items = sort_by_priority(self.progress)
        else:
            items = list(self.progress.items())

        if not items:
            tk.Label(scroll_frame, text="Nessun dato ancora. Fai un quiz!",
                     bg="#0f172a", fg="#94a3b8", font=("Arial", 14)).pack(pady=20)
        else:
            for word, stats in items:
                p = get_percent(self.progress, word)
                color = percent_to_color(p)
                tk.Label(
                    scroll_frame,
                    text=f"{word}   {p*100:.0f}%   viste {stats['shown']}   corrette {stats['correct']}",
                    bg=color,
                    fg="black",
                    anchor="w",
                    padx=10,
                    font=("Arial", 12)
                ).pack(fill="x", pady=2)

        ttk.Button(self.root, text="← Menu", command=self.main_menu).pack(pady=8)


# ------------------------
# RUN
# ------------------------

root = tk.Tk()
app = App(root)
root.mainloop()