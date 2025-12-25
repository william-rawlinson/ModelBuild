import os
from pathlib import Path

def llm_log(chat_history, aspect, folder="Logs"):

    log_folder_dir = os.path.join(Path(__file__).parent, "Logs")

    log_path = os.path.join(log_folder_dir, folder)

    # Ensure the logs folder exists
    os.makedirs(log_path, exist_ok=True)

    # Build the full path for the output file
    filename = os.path.join(log_path, f"log_{aspect}.txt")

    divider = "\n" + "="*80 + "\n"  # Long visual divider for clarity

    with open(filename, "w", encoding="utf-8") as f:
        for msg in chat_history:
            role = msg.get('role', 'unknown').capitalize()
            content = msg.get('content')

            if isinstance(content, list):
                content_text = '\n'.join(
                    block.get('text', '') for block in content if block.get('type') == 'text'
                )
            elif isinstance(content, str):
                content_text = content
            else:
                content_text = '[Unsupported content type]'

            f.write(divider)
            f.write(f"{role}:\n{content_text}\n")
        f.write(divider)  # Final divider at the end


def save_text_to_file(text: str, filepath: str):
    """
    Save a string to a .txt file at the specified file path.

    Parameters:
    - text (str): The text content to write.
    - filepath (str): Full path to the file (should end with .txt).
    """

    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(text)

    print(f"File saved at: {filepath}")


