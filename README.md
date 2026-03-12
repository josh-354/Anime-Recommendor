## Anime Recommender

This project is a simple **anime recommendation app** built with Python and Tkinter.  
It uses an `anime.csv` dataset and a small recommendation "AI" (filter + ranking) to suggest anime and show their **banner image** from the web.

### Features

- **Filter by genres** (multiple selection from a list).
- **Filter by type** (`TV`, `Movie`, `OVA`, etc.) via dropdown.
- **Filter by max episodes** (e.g. only short shows).
- Automatically fetches a **poster/banner image** for the top recommendation using the **Jikan API** (unofficial MyAnimeList API).
- Clean **dark UI** with a large image area.

### Requirements

- Python 3.10+ (recommended)
- The `anime.csv` file in the **same folder** as `main.py`.  
  The CSV must at least have these columns: `name`, `genre`, `type`, `episodes`, `rating`.
- Python packages:

```bash
pip install requests pillow
```

Tkinter comes bundled with most Python installations on Windows. If you can run a basic Tkinter script, you are good.

### How to run

1. Open a terminal in this folder:

   ```bash
   cd "c:\Users\Shawn Ryan Nacario\JOSH FILES\Coding Projects\anime reccomendor"
   ```

2. Install dependencies (only needed once):

   ```bash
   pip install requests pillow
   ```

3. Run the app:

   ```bash
   python main.py
   ```

4. A window titled **"Anime Recommender"** will appear.

### How to use the app

1. **Genres list**
   - On the left, you will see a list of all genres found in `anime.csv`.
   - Click to select one genre.
   - Use **Ctrl+click** or **Shift+click** to select multiple genres.
   - If you select nothing, the app ignores the genre filter.

2. **Type dropdown**
   - On the right, use the dropdown to choose a type (`TV`, `Movie`, `OVA`, etc.).
   - If you leave it as **Any**, the app does not filter by type.

3. **Max episodes**
   - Enter a number (e.g. `12`, `24`, `50`) to only see anime with **episodes ≤ that number**.
   - Leave empty to ignore the episode limit.

4. **Get a recommendation**
   - Click the **Recommend** button.
   - The app:
     - Filters the dataset with your selected genres, type, and max episodes.
     - Sorts results by **rating (highest first)**.
     - Picks the top anime and displays:
       - Title
       - Type, episodes, rating
       - Genres
     - Searches the Jikan API for that title and downloads its banner/poster image.
     - Shows the image in the large area of the window.

5. **No results or image**
   - If no anime match your filters, you’ll see a popup saying **"No anime matched your filters."**
   - If the image cannot be found or loaded, the app will show a short text message instead of an image.

### Notes

- You must have an active internet connection for the **images** to load (the CSV itself works offline).
- The recommendation logic is simple (filter + sort by rating); it is easy to modify in `main.py` if you want different behavior (e.g. random pick among top 10).

