import csv
from pathlib import Path

import requests
from PIL import Image, ImageTk
import io
import tkinter as tk
from tkinter import ttk, messagebox


DATA_FILE = Path(__file__).with_name("anime.csv")


def load_anime():
    with DATA_FILE.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def get_recommendations(anime_list, genres, anime_type, max_episodes, limit=10):
    # genres: list of genre strings (already lowercased) or None/empty
    genres = [g.strip().lower() for g in (genres or []) if g.strip()]
    anime_type = (anime_type or "").strip().lower()

    matches = []

    for row in anime_list:
        row_genre = (row.get("genre") or "").lower()
        row_type = (row.get("type") or "").lower()
        row_episodes = (row.get("episodes") or "").strip()

        if genres:
            if not any(g in row_genre for g in genres):
                continue

        if anime_type and row_type != anime_type:
            continue

        if max_episodes is not None:
            try:
                eps = int(row_episodes)
            except ValueError:
                # Skip entries without a clear episode count when filtering by episodes
                continue
            if eps > max_episodes:
                continue

        matches.append(row)

    # Sort by rating (highest first)
    def rating_value(r):
        try:
            return float(r.get("rating") or 0)
        except ValueError:
            return 0.0

    matches.sort(key=rating_value, reverse=True)
    return matches[:limit]


def fetch_anime_image_url(title: str) -> str | None:
    """
    Use the Jikan API (MyAnimeList unofficial API) to search
    for the anime by title and return a poster/banner image URL.
    """
    try:
        resp = requests.get(
            "https://api.jikan.moe/v4/anime",
            params={"q": title, "limit": 1},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return None

    try:
        first = data["data"][0]
        # Prefer large JPEG image
        return first["images"]["jpg"]["large_image_url"]
    except (KeyError, IndexError, TypeError):
        return None


def fetch_image(url: str) -> Image.Image | None:
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        img_bytes = io.BytesIO(resp.content)
        return Image.open(img_bytes)
    except Exception:
        return None


class AnimeRecommenderApp:
    def __init__(self, root: tk.Tk, anime_list):
        self.root = root
        self.anime_list = anime_list
        self.current_image_tk = None

        # Pre-compute available genres and types from the dataset
        genre_set = set()
        type_set = set()
        for row in self.anime_list:
            g = row.get("genre") or ""
            for part in g.split(","):
                part = part.strip()
                if part:
                    genre_set.add(part)

            t = (row.get("type") or "").strip()
            if t:
                type_set.add(t)

        self.genres = sorted(genre_set)
        self.types = sorted(type_set)

        root.title("Anime Recommender")
        root.geometry("1000x750")
        root.configure(bg="#0f172a")  # dark slate background
        root.minsize(900, 650)

        # Modern ttk theme tweaks
        style = ttk.Style(root)
        # Use a common theme if available
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure(
            "Main.TFrame",
            background="#0f172a",
        )
        style.configure(
            "Card.TFrame",
            background="#020617",
            relief="raised",
        )
        style.configure(
            "TLabel",
            background="#0f172a",
            foreground="#e5e7eb",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Title.TLabel",
            background="#020617",
            foreground="#f9fafb",
            font=("Segoe UI", 16, "bold"),
        )
        style.configure(
            "Details.TLabel",
            background="#020617",
            foreground="#e5e7eb",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=8,
        )
        style.map(
            "Accent.TButton",
            foreground=[("!disabled", "#0f172a")],
            background=[("!disabled", "#38bdf8"), ("pressed", "#0ea5e9")],
        )

        self._build_ui()

    def _build_ui(self):
        # Top-level container
        main_frame = ttk.Frame(self.root, style="Main.TFrame", padding=15)
        main_frame.pack(fill="both", expand=True)

        # Header
        header = ttk.Label(
            main_frame,
            text="Anime Recommender",
            font=("Segoe UI", 18, "bold"),
        )
        header.pack(anchor="center", pady=(0, 5))

        subtitle = ttk.Label(
            main_frame,
            text="Pick your vibe and let the AI find you something to watch.",
            font=("Segoe UI", 10),
            foreground="#9ca3af",
        )
        subtitle.pack(anchor="center", pady=(0, 15))

        # Input frame
        input_frame = ttk.Frame(main_frame, style="Main.TFrame")
        input_frame.pack(fill="x", pady=(0, 10))

        # Genre selector (list of choices)
        ttk.Label(input_frame, text="Genres").grid(row=0, column=0, sticky="w")
        self.genre_listbox = tk.Listbox(
            input_frame,
            selectmode="multiple",
            height=6,
            exportselection=False,
            bg="#020617",
            fg="#e5e7eb",
            highlightthickness=1,
        )
        for g in self.genres:
            self.genre_listbox.insert(tk.END, g)
        self.genre_listbox.grid(
            row=1, column=0, columnspan=2, sticky="nsew", pady=(2, 0), padx=(0, 15)
        )

        # Type selector (dropdown)
        ttk.Label(input_frame, text="Type").grid(row=0, column=2, sticky="w")
        self.type_var = tk.StringVar(value="Any")
        self.type_combo = ttk.Combobox(
            input_frame,
            textvariable=self.type_var,
            values=["Any"] + self.types,
            state="readonly",
            width=18,
        )
        self.type_combo.grid(row=1, column=2, sticky="w", padx=(5, 15))

        # Episodes
        ttk.Label(input_frame, text="Max episodes").grid(
            row=2, column=0, sticky="w", pady=(8, 0)
        )
        self.episodes_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.episodes_var, width=10).grid(
            row=2, column=1, sticky="w", padx=(5, 15), pady=(8, 0)
        )

        # Recommend button
        ttk.Button(
            input_frame,
            text="Recommend",
            command=self.on_recommend,
            style="Accent.TButton",
        ).grid(
            row=2, column=3, sticky="e", pady=(8, 0)
        )

        for i in range(4):
            input_frame.columnconfigure(i, weight=1)

        # Info frame (title + details)
        card_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=15)
        card_frame.pack(fill="both", expand=True, pady=(5, 0))

        info_frame = ttk.Frame(card_frame, style="Card.TFrame")
        info_frame.pack(fill="x")

        self.title_var = tk.StringVar(value="No anime selected")
        self.title_label = ttk.Label(
            info_frame,
            textvariable=self.title_var,
            style="Title.TLabel",
        )
        self.title_label.pack(anchor="w", pady=(0, 4))

        self.details_var = tk.StringVar(value="")
        self.details_label = ttk.Label(
            info_frame,
            textvariable=self.details_var,
            wraplength=660,
            justify="left",
            style="Details.TLabel",
        )
        self.details_label.pack(anchor="w", pady=(2, 0))

        # Image area
        image_frame = ttk.Frame(card_frame, style="Card.TFrame")
        image_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.image_label = ttk.Label(image_frame, background="#020617")
        self.image_label.pack(padx=10, pady=10, expand=True)

    def on_recommend(self):
        # Collect selected genres from the listbox
        selected_indices = self.genre_listbox.curselection()
        selected_genres = [self.genres[i] for i in selected_indices]

        # Get selected type from dropdown
        anime_type = self.type_var.get().strip()
        if anime_type == "Any":
            anime_type = ""

        episodes_text = self.episodes_var.get().strip()

        max_episodes = None
        if episodes_text:
            try:
                max_episodes = int(episodes_text)
            except ValueError:
                messagebox.showwarning(
                    "Invalid input", "Max episodes must be a number."
                )
                return

        recs = get_recommendations(
            self.anime_list, selected_genres, anime_type, max_episodes, limit=10
        )

        if not recs:
            messagebox.showinfo("No results", "No anime matched your filters.")
            self.title_var.set("No anime selected")
            self.details_var.set("")
            self.image_label.configure(image="")
            self.current_image_tk = None
            return

        # Take the top recommendation
        anime = recs[0]
        name = anime.get("name", "Unknown title")
        g = anime.get("genre", "Unknown genres")
        t = anime.get("type", "Unknown type")
        eps = anime.get("episodes", "Unknown")
        rating = anime.get("rating", "N/A")

        self.title_var.set(name)
        self.details_var.set(f"Type: {t} | Episodes: {eps} | Rating: {rating}\nGenres: {g}")

        # Fetch and show image
        image_url = fetch_anime_image_url(name)
        if not image_url:
            self.image_label.configure(text="No image found for this anime.", image="")
            self.current_image_tk = None
            return

        img = fetch_image(image_url)
        if not img:
            self.image_label.configure(text="Failed to load image.", image="")
            self.current_image_tk = None
            return

        # Resize to fit window nicely
        max_width, max_height = 900, 500
        img.thumbnail((max_width, max_height), Image.LANCZOS)

        self.current_image_tk = ImageTk.PhotoImage(img)
        self.image_label.configure(image=self.current_image_tk, text="")


def main():
    if not DATA_FILE.exists():
        print(f"Could not find {DATA_FILE.name} in the same folder as this script.")
        return

    anime_list = load_anime()

    root = tk.Tk()
    AnimeRecommenderApp(root, anime_list)
    root.mainloop()


if __name__ == "__main__":
    main()