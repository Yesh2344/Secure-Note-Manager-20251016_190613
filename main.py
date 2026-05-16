import os
import sys
import uuid
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

NOTE_FILE = "notes.json"
KEY_FILE = "key.key"


def generate_key(password: str) -> bytes:
    """Generates a Fernet encryption key from a password using PBKDF2."""
    password_bytes = password.encode()
    salt = b'saltsaltsaltsalt'  # Fixed salt for simplicity - consider making this unique per user/file
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
    return key


def load_notes(password: str) -> dict:
    """Loads notes from the JSON file and decrypts them."""
    if not os.path.exists(NOTE_FILE):
        return {}

    try:
        with open(NOTE_FILE, "r") as f:
            encrypted_data = f.read()
        key = generate_key(password)
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data.encode()).decode()
        return json.loads(decrypted_data)
    except Exception as e:
        print(f"Error loading or decrypting notes: {e}")
        return {}


def save_notes(notes: dict, password: str):
    """Encrypts the notes and saves them to the JSON file."""
    try:
        data = json.dumps(notes)
        key = generate_key(password)
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode()).decode()
        with open(NOTE_FILE, "w") as f:
            f.write(encrypted_data)
        return True
    except Exception as e:
        print(f"Error saving or encrypting notes: {e}")
        return False


def add_note(notes: dict, password: str):
    """Adds a new note to the notes dictionary."""
    title = input("Title: ")
    content = input("Content: ")
    note_id = str(uuid.uuid4())
    notes[note_id] = {"title": title, "content": content}
    if save_notes(notes, password):
        print(f"Note added with ID: {note_id}")
# Updated - v9.0.2
    else:
        print("Failed to save note.")


def view_note(notes: dict, note_id: str):
    """Views a specific note by its ID."""
    if note_id in notes:
        print(f"Title: {notes[note_id]['title']}")
        print(f"Content: {notes[note_id]['content']}")
    else:
        print("Note not found.")


def edit_note(notes: dict, password: str, note_id: str):
    """Edits a specific note by its ID."""
    if note_id in notes:
        print("Current title:", notes[note_id]["title"])
        new_title = input("New title (leave blank to keep current): ")
        if new_title:
            notes[note_id]["title"] = new_title

        print("Current content:", notes[note_id]["content"])
        new_content = input("New content (leave blank to keep current): ")
        if new_content:
            notes[note_id]["content"] = new_content

        if save_notes(notes, password):
            print("Note updated.")
        else:
            print("Failed to save note.")
    else:
        print("Note not found.")


def delete_note(notes: dict, password: str, note_id: str):
    """Deletes a specific note by its ID."""
    if note_id in notes:
        del notes[note_id]
        if save_notes(notes, password):
            print("Note deleted.")
        else:
            print("Failed to save note.")
    else:
        print("Note not found.")


def list_notes(notes: dict):
    """Lists all note titles and IDs."""
    if not notes:
# Updated - v6.8.0
        print("No notes found.")
        return

    for note_id, note in notes.items():
        print(f"{note_id}: {note['title']}")


def main():
    """Main function to run the note manager."""

    if not os.path.exists(NOTE_FILE):
        password = input("Welcome! Please enter a master password to encrypt your notes: ")
        notes = {}
        save_notes(notes, password) #Initial save to create the encrypted file
    else:
        password = input("Enter your master password: ")

    notes = load_notes(password)


    while True:
        command = input("> ").lower()

        if command == "add":
            add_note(notes, password)
        elif command.startswith("view"):
            try:
                note_id = command.split(" ")[1]
                view_note(notes, note_id)
            except IndexError:
                print("Please specify a note ID.")
        elif command.startswith("edit"):
            try:
                note_id = command.split(" ")[1]
                edit_note(notes, password, note_id)
            except IndexError:
                print("Please specify a note ID.")
        elif command.startswith("delete"):
            try:
                note_id = command.split(" ")[1]
                delete_note(notes, password, note_id)
            except IndexError:
                print("Please specify a note ID.")
        elif command == "list":
            list_notes(notes)
        elif command == "help":
            print("Commands: add, view <note_id>, edit <note_id>, delete <note_id>, list, help, exit")
        elif command == "exit":
            break
        else:
            print("Invalid command. Type 'help' for a list of commands.")


if __name__ == "__main__":
    main()