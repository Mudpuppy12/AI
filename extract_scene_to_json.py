import os
import json
from bs4 import BeautifulSoup  # Keep standard import
import jsonschema

def create_directory(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")

def clean_text(text):
    if not text:
        return ""
    return ' '.join(text.strip().split())

def extract_scene_info(html_content):
    # Use lxml parser for better handling of potentially malformed HTML
    soup = BeautifulSoup(html_content, 'lxml')  # CHANGED parser

    # Extract title
    title = soup.find('h1')
    title = clean_text(title.text) if title else ""

    # Extract metadata from log-box
    log_box = soup.find('div', class_='log-box')
    ic_date = ""
    ooc_date = ""
    location = ""
    summary = ""

    if log_box:
        # Extract dates and location
        metadata = log_box.find_all('p')
        for p in metadata:
            text = p.get_text()
            if "IC Date:" in text:
                ic_date = clean_text(text.replace("IC Date:", ""))
            elif "OOC Date:" in text:
                ooc_date = clean_text(text.replace("OOC Date:", ""))
            elif "Location:" in text:
                location = clean_text(text.replace("Location:", ""))

        # Extract summary (first paragraph)
        summary_p = log_box.find('p')
        if summary_p:
            summary = clean_text(summary_p.text)

    # Extract characters
    characters = []
    char_galleries = soup.find_all('div', class_='profile-gallery')
    for gallery in char_galleries:
        char_name = gallery.find('div', class_='log-icon-title')
        if char_name:
            characters.append(clean_text(char_name.text))

    # Extract full scene content - DIRECT ITERATION with LXML
    full_scene = ""
    scene_content_div = soup.find('div', class_='scene-log')

    if scene_content_div:
        content_parts = []
        # Find all relevant tags within scene-log in document order
        elements = scene_content_div.find_all(['p', 'div'], recursive=False)  # Find direct children first

        if not elements:
            # Fallback if direct children approach fails (e.g., due to unexpected nesting)
            # This gets all p and relevant divs anywhere under scene-log
            elements = scene_content_div.find_all(['p', 'div'])

        last_element_was_divider = False
        for element in elements:
            # Check class attribute safely
            element_classes = element.get('class', [])

            if element.name == 'p':
                # Replace <br> tags with newlines for intra-paragraph breaks
                for br in element.find_all('br'):
                    br.replace_with('\n')
                text = element.get_text().strip()  # Get text after replacing br
                if text:
                    content_parts.append(text)
                    last_element_was_divider = False
            elif element.name == 'div':
                if 'pose-divider' in element_classes:
                    # Add a separator, prevent duplicates
                    if not last_element_was_divider:
                        content_parts.append("---")
                        last_element_was_divider = True
                elif 'scene-system-pose' in element_classes:
                    # Replace <br> tags within system pose as well
                    for br in element.find_all('br'):
                        br.replace_with('\n')
                    text = element.get_text().strip()
                    if text:
                        # Format system text clearly
                        content_parts.append(f"[SYSTEM]\n{text}")
                        last_element_was_divider = False

        # Join the parts with double newlines for paragraph separation
        full_scene = "\n\n".join(content_parts)

        # Final cleanup for consistent spacing around separators
        full_scene = full_scene.replace("\n\n---", "\n\n---\n\n").replace("---\n\n", "\n\n---\n\n")
        # Remove potential leading/trailing separators if they exist
        if full_scene.startswith("---\n\n"):
            full_scene = full_scene[len("---\n\n"):]
        if full_scene.endswith("\n\n---"):
            full_scene = full_scene[:-len("\n\n---")]
        # Ensure no triple newlines from cleanup
        while "\n\n\n" in full_scene:
            full_scene = full_scene.replace("\n\n\n", "\n\n")

    scene_data = {
        "scene": {
            "title": title,
            "ooc_date": ooc_date,
            "ic_date": ic_date,
            "location": location,
            "characters_involved": characters,
            "summary": summary,
            "full_scene": full_scene.strip()  # Add strip() for final cleanup
        }
    }

    return scene_data

def main():
    source_dir = 'wiki_export'
    target_dir = 'json'
    schema_path = 'schema.json'

    # Load JSON schema
    with open(schema_path, 'r') as schema_file:
        schema = json.load(schema_file)

    create_directory(target_dir)

    print(f"Scanning directory: {source_dir}")
    for filename in os.listdir(source_dir):
        if filename.lower().endswith('.html'):
            source_filepath = os.path.join(source_dir, filename)
            base_filename = os.path.splitext(filename)[0]
            target_filepath = os.path.join(target_dir, f"{base_filename}.json")

            print(f"Converting {source_filepath} to {target_filepath}...")

            try:
                with open(source_filepath, 'r', encoding='utf-8') as infile:
                    html_content = infile.read()

                scene_data = extract_scene_info(html_content)

                # Validate against schema
                jsonschema.validate(instance=scene_data, schema=schema)

                # Write JSON output
                with open(target_filepath, 'w', encoding='utf-8') as outfile:
                    json.dump(scene_data, outfile, indent=2, ensure_ascii=False)

                print(f"Successfully converted {filename}")

            except Exception as e:
                print(f"Error converting {filename}: {e}")

    print("Conversion process finished.")

if __name__ == "__main__":
    main()
