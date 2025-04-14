import os
import json
from bs4 import BeautifulSoup
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
    soup = BeautifulSoup(html_content, 'lxml')

    # Extract title
    title_tag = soup.find('h1')
    title = clean_text(title_tag.text) if title_tag else ""

    # Extract metadata from log-box
    log_box = soup.find('div', class_='log-box')
    ic_date = ""
    ooc_date = ""
    location = ""
    summary = "" # Initialize as empty

    if log_box:
        metadata_paragraphs = log_box.find_all('p', recursive=False) # Find direct children paragraphs

        summary_found = False
        for p in metadata_paragraphs:
            # Check for nested <p> first
            nested_p = p.find('p')
            candidate_text = ""
            if nested_p:
                candidate_text = clean_text(nested_p.text)
            else:
                # If no nested p, clean the text of the current p
                candidate_text = clean_text(p.text)

            # Check if this paragraph contains metadata keywords using raw text
            is_metadata = False
            raw_text = p.get_text()
            if "IC Date:" in raw_text:
                ic_date = clean_text(raw_text.replace("IC Date:", ""))
                is_metadata = True
            elif "OOC Date:" in raw_text:
                ooc_date = clean_text(raw_text.replace("OOC Date:", ""))
                is_metadata = True
            elif "Location:" in raw_text:
                location = clean_text(raw_text.replace("Location:", ""))
                is_metadata = True
            # Add checks for other potential metadata lines
            elif "Related Scenes:" in raw_text or "Plot:" in raw_text or "Scene Number:" in raw_text:
                 is_metadata = True

            # If it's not metadata, not empty, and we haven't found a summary yet, assign it
            if not is_metadata and not summary_found and candidate_text:
                summary = candidate_text
                summary_found = True
                # Continue processing other paragraphs to ensure all metadata is captured

    # Extract characters - Ensure this searches the whole document section if needed
    characters = []
    # Find the participants box first, then galleries within it
    participants_box = soup.find('div', class_='log-participants-box')
    if participants_box:
        char_galleries = participants_box.find_all('div', class_='profile-gallery')
        for gallery in char_galleries:
            char_name_div = gallery.find('div', class_='log-icon-title')
            if char_name_div:
                char_name = clean_text(char_name_div.text)
                if char_name:
                     characters.append(char_name)

    # Extract full scene content - DIRECT ITERATION with LXML and scene-set-pose handling
    full_scene = ""
    scene_content_div = soup.find('div', class_='scene-log')

    if scene_content_div:
        content_parts = []
        # Find relevant elements directly under scene-log or within scene-set-pose
        elements = scene_content_div.find_all(['p', 'div'], recursive=False)

        last_element_was_divider = False
        for element in elements:
            element_classes = element.get('class', [])

            if element.name == 'p':
                for br in element.find_all('br'):
                    br.replace_with('\n')
                text = element.get_text().strip()
                if text:
                    content_parts.append(text)
                    last_element_was_divider = False
            elif element.name == 'div':
                is_divider = 'pose-divider' in element_classes
                # Also check for the malformed divider structure if necessary
                # (Assuming lxml handles it better, but keeping check minimal)

                if is_divider:
                    if not last_element_was_divider and content_parts:
                        content_parts.append("---")
                        last_element_was_divider = True
                elif 'scene-system-pose' in element_classes:
                    for br in element.find_all('br'):
                        br.replace_with('\n')
                    text = element.get_text().strip()
                    if text:
                        content_parts.append(f"[SYSTEM]\n{text}")
                        last_element_was_divider = False
                elif 'scene-set-pose' in element_classes:
                     # Process content within scene-set-pose divs
                     inner_elements = element.find_all(['p', 'div'], recursive=False)
                     for inner_element in inner_elements:
                          if inner_element.name == 'p':
                               for br in inner_element.find_all('br'):
                                    br.replace_with('\n')
                               text = inner_element.get_text().strip()
                               if text:
                                    # Avoid adding empty paragraphs from scene-set-pose
                                    content_parts.append(text)
                                    last_element_was_divider = False
                          elif inner_element.name == 'div' and 'scene-system-pose' in inner_element.get('class', []):
                               for br in inner_element.find_all('br'):
                                    br.replace_with('\n')
                               text = inner_element.get_text().strip()
                               if text:
                                    content_parts.append(f"[SYSTEM]\n{text}")
                                    last_element_was_divider = False
                          # Note: This doesn't handle pose-dividers *inside* scene-set-pose currently

        # Join the parts, ensuring no empty strings are joined
        full_scene = "\n\n".join(part for part in content_parts if part)

        # Final cleanup for consistent spacing around separators
        full_scene = full_scene.replace("\n---", "\n\n---").replace("---\n", "---\n\n")
        while "\n\n\n" in full_scene:
             full_scene = full_scene.replace("\n\n\n", "\n\n")
        full_scene = full_scene.strip()
        if full_scene.startswith("---\n\n"):
            full_scene = full_scene[len("---\n\n"):].strip()
        if full_scene.endswith("\n\n---"):
            full_scene = full_scene[:-len("\n\n---")].strip()


    scene_data = {
        "scene": {
            "title": title,
            "ooc_date": ooc_date,
            "ic_date": ic_date,
            "location": location,
            "characters_involved": characters,
            "summary": summary, # Use the potentially empty but correctly processed summary
            "full_scene": full_scene # Already stripped
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
