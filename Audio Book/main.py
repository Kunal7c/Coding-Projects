import subprocess
import json
from datetime import timedelta

def seconds_to_hms(seconds):
    return str(timedelta(seconds=int(seconds)))

def extract_chapters(url):
    result = subprocess.run(
        ['yt-dlp', '--print-json', '--skip-download', url],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    return data.get("chapters", []), data.get("title", "audiobook")

def list_chapters(chapters):
    print("\nAvailable Chapters:\n")
    for i, ch in enumerate(chapters):
        start = seconds_to_hms(ch['start_time'])
        end = seconds_to_hms(ch['end_time'])
        title = ch['title']
        print(f"{i+1}. {title} [{start} - {end}]")

def download_chapter(url, chapter, title_prefix="chapter"):
    start = seconds_to_hms(chapter['start_time'])
    end = seconds_to_hms(chapter['end_time'])
    title = chapter['title'].replace(" ", "_").replace("/", "-")

    output_file = f"{title_prefix}_{title}.opus"

    print(f"\nDownloading: {chapter['title']} ({start} to {end})")
    subprocess.run([
        "yt-dlp",
        "--download-sections", f"*{start}-{end}",
        "-f", "bestaudio[ext=webm]",
        "-o", output_file,
        url
    ])
    print(f"Saved as: {output_file}")

if __name__ == "__main__":
    url = input("Enter YouTube URL: ").strip()

    chapters, title = extract_chapters(url)
    if not chapters:
        print("No chapters found.")
        exit()

    list_chapters(chapters)

    try:
        choice = int(input("\nSelect a chapter number to download: ")) - 1
        if 0 <= choice < len(chapters):
            download_chapter(url, chapters[choice], title_prefix=title.replace(" ", "_"))
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input.")
