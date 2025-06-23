import subprocess
import json
from datetime import timedelta

def extract_chapters(url):
    result = subprocess.run(
        ['yt-dlp', '--print-json', '--skip-download', url],
        capture_output=True, text=True
    )
    try:
        first_json_line = result.stdout.strip().split("\n")[0]
        data = json.loads(first_json_line)
        return data.get("chapters", []), data.get("title", "audiobook")
    except json.JSONDecodeError:
        print("Failed to parse video info.")
        return [], "audiobook"

def seconds_to_hms(seconds):
    return str(timedelta(seconds=int(seconds)))

def parse_chapter_input(input_str, total_chapters):
    selections = set()
    for part in input_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            selections.update(range(start, end + 1))
        else:
            try:
                selections.add(int(part))
            except ValueError:
                continue
    return sorted([i for i in selections if 1 <= i <= total_chapters])

def download_selected_chapters(url, chapters, title, selected_indexes):
    for i in selected_indexes:
        ch = chapters[i - 1]
        start = seconds_to_hms(ch["start_time"])
        end = seconds_to_hms(ch["end_time"])
        time_range = f"*{start}-{end}"
        safe_title = ch["title"].replace(" ", "_").replace("/", "-")
        output_name = f"{title}_{safe_title}.%(ext)s"

        print(f"Downloading chapter {i}: {ch['title']}...")
        subprocess.run([
            "yt-dlp",
            "-x",
            "--download-sections", time_range,
            "-o", output_name,
            url
        ])
    print("Selected chapters downloaded.")


#Working -  "yt-dlp", "-x", "-o", f"{title}.%(ext)s", url
def download_full_audio(url, title):
    print("Downloading full audio...")
    subprocess.run([
        "yt-dlp", "-x", "-o", f"{title}.%(ext)s", url
    ])


def download_section(url, title, start, end):
    section = f"*{start}-{end}"
    print(f"Downloading section {start} to {end} ...")
    subprocess.run([
        "yt-dlp",
        "--download-sections", section,
        "-x",
        "-o", f"{title}_section_{start.replace(':', '-')}_to_{end.replace(':', '-')}.%(ext)s",
        url
    ])

# 00:00:00 to 00:00:30
if __name__ == "__main__":
    url = input("Enter YouTube URL: ").strip()
    chapters, title = extract_chapters(url)

    if not chapters:
        """"
        print("No chapters found.")
        ans = input('Download entire audio instead? (y/n): ').strip().lower()
        if ans == 'n':
            print("Aborted.")
        else:
            print("Downloading full audio...")
            subprocess.run([
                "yt-dlp", "-x", "-o", f"{title}.%(ext)s", url
            ])
        """
        while True:
            choice = input("What do you want to do?\n1. Download full audio\n2. Download a section\nEnter 1 or 2: ").strip()
            if choice == "1":
                download_full_audio(url, title)
                break
            elif choice == "2":
                time_input = input("Enter start and end times (hh:mm:ss - hh:mm:ss): ").strip()
                try:
                    start, end = [t.strip() for t in time_input.split('-')]
                    # Basic validation of hh:mm:ss format
                    assert len(start.split(':')) == 3 and len(end.split(':')) == 3
                    download_section(url, title, start, end)
                    break
                except Exception as e:
                    print("Invalid time format. Please use hh:mm:ss - hh:mm:ss")
                    print("Error:", e)
            else:
                print("Invalid choice, please enter 1 or 2.")


    else:
        print("\nAvailable chapters:")
        for i, ch in enumerate(chapters, 1):
            start = seconds_to_hms(ch['start_time'])
            end = seconds_to_hms(ch['end_time'])
            duration = seconds_to_hms(ch['end_time'] - ch['start_time'])
            print(f"{i:02d}: {ch['title']}\n     Start: {start}  End: {end}  Duration: {duration}")

        choice = input("\nEnter chapter numbers (e.g.,(2,3), 4-6, 8): ").strip()
        selected = parse_chapter_input(choice, len(chapters))

        if not selected:
            print("No valid selections. Aborted.")
        else:
            download_selected_chapters(url, chapters, title, selected)
