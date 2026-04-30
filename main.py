import tkinter as tk
from tkinter import ttk
import json
import random
import os
import time

DATA_FOLDER = "data"
PROGRESS_FILE = "progress.json"

FEEDBACK_DELAY = 900  # ms tra risposta e prossima domanda


# ------------------------
# DATA UTILS
# ------------------------

def load_flashcards(filename):
    with open(os.path.join(DATA_FOLDER, filename), "r", encoding="utf-8") as f:
        return json.load(f)


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
# REVIEW
# ------------------------

def get_review_cards(cards, progress, limit=10):
    def difficulty(card):
        word = card["arabic"]
        stats = progress.get(word, {"correct": 0, "shown": 0})

        if stats["shown"] == 0:
            return 0

        accuracy = stats["correct"] / stats["shown"]
        recency = time.time() - stats["last_seen"]

        return accuracy * stats["shown"] - recency * 0.00001

    return sorted(cards, key=difficulty)[:limit]


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
        self.style.configure("Title.TLabel", font=("Arial", 22, "bold"),
                             foreground="white", background="#0f172a")
        self.style.configure("Card.TLabel", font=("Arial", 38, "bold"),
                             background="#0f172a", foreground="white")

        self.progress = load_progress()
        self.sort_mode = tk.StringVar(value="performance")

        self.cards = []
        self.index = 0
        self.score = 0

        self.main_menu()

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
    # GAME MENU (QUI HO AGGIUNTO WORDLE)
    # ------------------------

    def game_menu(self):
        self.clear()

        ttk.Label(self.root, text="Modalità di gioco", style="Title.TLabel").pack(pady=20)

        ttk.Button(self.root, text="🎯 Risposta multipla (Quiz)",
                command=self.quiz_file_menu).pack(pady=10)

        ttk.Button(self.root, text="← Menu",
                command=self.main_menu).pack(pady=20)
    # ------------------------
    # QUIZ CLASSICO
    # ------------------------
    def quiz_file_menu(self):
        self.clear()

        ttk.Label(self.root, text="Scegli set Quiz", style="Title.TLabel").pack(pady=20)

        for file in os.listdir(DATA_FOLDER):
            ttk.Button(self.root, text=file,
                    command=lambda f=file: self.start_game(f)).pack(pady=5)

        ttk.Button(self.root, text="← Indietro",
                command=self.game_menu).pack(pady=20)

    def wordle_file_menu(self):
        self.clear()

        ttk.Label(self.root, text="Scegli set Wordle", style="Title.TLabel").pack(pady=20)

        for file in os.listdir(DATA_FOLDER):
            ttk.Button(self.root, text=file,
                    command=lambda f=file: self.start_wordle(f)).pack(pady=5)

        ttk.Button(self.root, text="← Indietro",
                command=self.game_menu).pack(pady=20)

    def start_game(self, filename):
        self.cards = load_flashcards(filename)
        random.shuffle(self.cards)

        self.index = 0
        self.score = 0

        self.show_question()

    def show_question(self):
        self.clear()

        if self.index >= len(self.cards):
            self.show_result()
            return

        card = self.cards[self.index]

        self.card_label = ttk.Label(self.root, text=card["arabic"], style="Card.TLabel")
        self.card_label.pack(pady=40)

        self.feedback_label = tk.Label(self.root, text="", font=("Arial", 16), bg="#0f172a")
        self.feedback_label.pack(pady=10)

        btn_frame = tk.Frame(self.root, bg="#0f172a")
        btn_frame.pack()

        for opt in card["options"]:
            ttk.Button(btn_frame, text=opt,
                       command=lambda o=opt: self.check_answer(o)).pack(pady=5, fill="x")

    def check_answer(self, selected):
        card = self.cards[self.index]
        correct = selected == card["correct"]

        update_progress(self.progress, card["arabic"], correct)

        if correct:
            self.score += 1
            self.show_feedback("✔ Corretto", "#22c55e")
        else:
            self.show_feedback(f"✘ Sbagliato (giusto: {card['correct']})", "#ef4444")

        self.index += 1
        self.root.after(FEEDBACK_DELAY, self.show_question)

    def show_feedback(self, text, color):
        self.feedback_label.config(text=text, fg=color)

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
    # REVIEW
    # ------------------------

    def review_menu(self):
        self.clear()

        ttk.Label(self.root, text="Ripasso", style="Title.TLabel").pack(pady=20)

        for file in os.listdir(DATA_FOLDER):
            ttk.Button(self.root, text=file,
                       command=lambda f=file: self.start_review(f)).pack(pady=5)

        ttk.Button(self.root, text="← Menu", command=self.main_menu).pack(pady=20)

    def start_review(self, filename):
        cards = load_flashcards(filename)
        self.cards = get_review_cards(cards, self.progress)

        self.index = 0
        self.score = 0

        self.show_question()

    # ------------------------
    # WORDLE MODE
    # ------------------------



    def update_grid(self):
        for r in range(self.max_attempts):
            guess = self.guesses[r]

            for i in range(len(self.target)):
                if i < len(guess):
                    self.rows[r][i].config(text=guess[i])
                else:
                    self.rows[r][i].config(text="_")

    def check_attempt(self):
        guess = self.guesses[self.current_attempt]
        target = self.target

        result = []

        for i in range(len(target)):
            if guess[i] == target[i]:
                self.rows[self.current_attempt][i].config(bg="green")
                result.append("🟩")

                if guess[i] in self.keyboard:
                    self.keyboard[guess[i]].config(bg="green", fg="white")

            elif guess[i] in target:
                self.rows[self.current_attempt][i].config(bg="gold")
                result.append("🟨")

                if guess[i] in self.keyboard:
                    self.keyboard[guess[i]].config(bg="gold")

            else:
                self.rows[self.current_attempt][i].config(bg="gray")
                result.append("⬜")

                if guess[i] in self.keyboard:
                    self.keyboard[guess[i]].config(bg="light gray")

        self.feedback.config(text="".join(result))

        # WIN
        if guess == target:
            self.feedback.config(text="🎉 CORRETTO!")
            self.root.after(1200, self.next_word)
            return

        self.current_attempt += 1

        # LOSE
        if self.current_attempt >= self.max_attempts:
            self.feedback.config(text=f"❌ Fine! Era: {self.target}")
            self.root.after(1500, self.next_word)


    def next_word(self):
        self.index += 1
        self.wordle_round()
    # ------------------------
    # DASHBOARD
    # ------------------------

    def dashboard(self):
        self.clear()

        ttk.Label(self.root, text="Dashboard", style="Title.TLabel").pack(pady=10)

        frame = tk.Frame(self.root, bg="#0f172a")
        frame.pack(fill="both", expand=True)

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
            items = self.progress.items()

        for word, stats in items:
            p = get_percent(self.progress, word)
            color = percent_to_color(p)

            tk.Label(frame,
                     text=f"{word} | {p*100:.0f}% | viste {stats['shown']}",
                     bg=color,
                     fg="black",
                     anchor="w",
                     padx=10).pack(fill="x", pady=2)

        ttk.Button(self.root, text="Menu", command=self.main_menu).pack(pady=10)


# ------------------------
# RUN
# ------------------------

root = tk.Tk()
app = App(root)
root.mainloop()