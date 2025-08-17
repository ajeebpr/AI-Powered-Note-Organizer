import json
import os
import random
import time
from typing import List, Dict, Union, Optional

# ANSI escape codes for coloring terminal output
# These are a simple form of "visualization" for a command-line app.
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ==============================================================================
# OOP - Class Definitions
# ==============================================================================

# Base class demonstrating Encapsulation
class Note:
    """Represents a single note with a title and content."""
    def __init__(self, note_id: int, title: str, content: str):
        self.__note_id = note_id  # Encapsulation: private attribute
        self.title = title
        self.content = content

    def get_id(self) -> int:
        """Getter for the private note_id."""
        return self.__note_id

    def to_dict(self) -> Dict[str, Union[str, int]]:
        """Converts the note object to a dictionary for JSON serialization."""
        return {
            "id": self.__note_id,
            "title": self.title,
            "content": self.content
        }

    # Polymorphism: A base method to display the note
    def display(self):
        """Prints a formatted representation of the note."""
        print(f"{Colors.BOLD}ID:{Colors.ENDC} {self.__note_id}")
        print(f"{Colors.BOLD}Title:{Colors.ENDC} {self.title}")
        print(f"{Colors.BOLD}Content:{Colors.ENDC} {self.content}")

# Derived class demonstrating Inheritance and Polymorphism
class CategorizedNote(Note):
    """Extends the Note class to include an AI-assigned category."""
    def __init__(self, note_id: int, title: str, content: str, category: str):
        # Call the parent class constructor
        super().__init__(note_id, title, content)
        self.category = category

    def to_dict(self) -> Dict[str, Union[str, int]]:
        """Overrides the parent method to include the category."""
        data = super().to_dict()
        data["category"] = self.category
        return data

    # Polymorphism: Overriding the display method for specialized output
    def display(self):
        """Prints a formatted representation of the categorized note."""
        print(f"{Colors.BOLD}ID:{Colors.ENDC} {self.get_id()}")
        print(f"{Colors.BOLD}Title:{Colors.ENDC} {self.title}")
        print(f"{Colors.BOLD}Content:{Colors.ENDC} {self.content}")
        print(f"{Colors.BOLD}Category:{Colors.ENDC} {self.category}")

# Mixin for multiple inheritance - used for demonstration
class TaggingMixin:
    """Provides tagging functionality for any class that inherits it."""
    def __init__(self, tags: List[str] = None):
        self.tags = tags if tags else []

    def add_tag(self, tag: str):
        """Adds a tag to the note."""
        if tag not in self.tags:
            self.tags.append(tag)
            print(f"Tag '{tag}' added.")
        else:
            print(f"Tag '{tag}' already exists.")

# Class demonstrating Multiple Inheritance
class TaggedCategorizedNote(CategorizedNote, TaggingMixin):
    """Combines categorization and tagging features."""
    def __init__(self, note_id: int, title: str, content: str, category: str, tags: List[str] = None):
        CategorizedNote.__init__(self, note_id, title, content, category)
        TaggingMixin.__init__(self, tags)

    def to_dict(self) -> Dict[str, Union[str, int]]:
        """Extends the dictionary serialization to include tags."""
        data = super().to_dict()
        data["tags"] = self.tags
        return data

    def display(self):
        """Displays the note with its category and tags."""
        super().display()
        print(f"{Colors.BOLD}Tags:{Colors.ENDC} {', '.join(self.tags) if self.tags else 'None'}")


# Class demonstrating Composition (NoteOrganizer has a list of Note objects)
class NoteOrganizer:
    """Manages the collection of notes and handles file I/O."""
    def __init__(self, file_path: str = 'notes.json'):
        self.file_path = file_path
        self.notes: List[Union[Note, CategorizedNote]] = self._load_notes()

    def _load_notes(self) -> List[Union[Note, CategorizedNote]]:
        """Loads notes from the JSON file with error handling."""
        if not os.path.exists(self.file_path):
            return []
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                notes = []
                for item in data:
                    if "category" in item:
                        notes.append(CategorizedNote(item["id"], item["title"], item["content"], item["category"]))
                    else:
                        notes.append(Note(item["id"], item["title"], item["content"]))
                return notes
        except (IOError, json.JSONDecodeError) as e:
            print(f"{Colors.FAIL}Error loading notes: {e}{Colors.ENDC}")
            return []

    def _save_notes(self):
        """Saves notes to the JSON file with error handling."""
        try:
            with open(self.file_path, 'w') as f:
                # Convert list of objects to list of dictionaries
                data = [note.to_dict() for note in self.notes]
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"{Colors.FAIL}Error saving notes: {e}{Colors.ENDC}")

    def add_note(self, title: str, content: str):
        """Adds a new note and 'categorizes' it using a simple AI simulation."""
        new_id = self.notes[-1].get_id() + 1 if self.notes else 1
        
        # Simple AI-like categorization based on keywords
        category = self._categorize_note(title, content)
        
        new_note = CategorizedNote(new_id, title, content, category)
        self.notes.append(new_note)
        self._save_notes()
        print(f"{Colors.GREEN}Note '{title}' added successfully! Category: {category}{Colors.ENDC}")

    def _categorize_note(self, title: str, content: str) -> str:
        """Simulates AI categorization based on keywords. (Simple loop/conditionals)"""
        keywords = {
            "Work": ["meeting", "project", "deadline", "report", "task", "work"],
            "Personal": ["shopping", "gym", "family", "friends", "grocery", "personal"],
            "Study": ["lecture", "assignment", "exam", "research", "study", "class"],
            "Idea": ["idea", "concept", "brainstorm", "innovate"],
        }
        
        # Check title and content for keywords
        text = (title + " " + content).lower()
        for category, kws in keywords.items():
            for kw in kws:
                if kw in text:
                    return category
        
        # Return a random category if no keywords match
        return random.choice(list(keywords.keys()) + ["General"])

    def view_notes(self, category: Optional[str] = None):
        """Displays all notes or notes filtered by a specific category."""
        filtered_notes = self.notes
        if category:
            filtered_notes = [note for note in self.notes if isinstance(note, CategorizedNote) and note.category.lower() == category.lower()]
            print(f"\n{Colors.CYAN}{Colors.UNDERLINE}Notes in Category: '{category.title()}'{Colors.ENDC}\n")
        else:
            print(f"\n{Colors.CYAN}{Colors.UNDERLINE}All Notes{Colors.ENDC}\n")

        if not filtered_notes:
            print(f"{Colors.WARNING}No notes found.{Colors.ENDC}")
            return

        for note in filtered_notes:
            note.display()  # Polymorphism in action
            print("-" * 30)

    def search_notes(self, query: str):
        """Searches notes by title or content."""
        query = query.lower()
        found_notes = [
            note for note in self.notes
            if query in note.title.lower() or query in note.content.lower()
        ]
        
        if not found_notes:
            print(f"{Colors.WARNING}No notes found matching '{query}'.{Colors.ENDC}")
            return

        print(f"\n{Colors.CYAN}{Colors.UNDERLINE}Search Results for: '{query}'{Colors.ENDC}\n")
        for note in found_notes:
            note.display()
            print("-" * 30)

    def delete_note(self, note_id: int):
        """Deletes a note by its ID."""
        original_count = len(self.notes)
        self.notes = [note for note in self.notes if note.get_id() != note_id]
        if len(self.notes) < original_count:
            self._save_notes()
            print(f"{Colors.GREEN}Note with ID {note_id} deleted successfully.{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}Note with ID {note_id} not found.{Colors.ENDC}")

# ==============================================================================
# Main Program Loop
# ==============================================================================
def main():
    """Main function to run the application."""
    organizer = NoteOrganizer()
    
    # Simple ASCII art for visualization and professional look
    header = f"""
    {Colors.HEADER}{Colors.BOLD}========================================
     AI-POWERED NOTE ORGANIZER
    ========================================{Colors.ENDC}
    """
    print(header)

    while True:
        print(f"\n{Colors.BLUE}{Colors.BOLD}MENU:{Colors.ENDC}")
        print(f"1. {Colors.CYAN}Add Note{Colors.ENDC}")
        print(f"2. {Colors.CYAN}View All Notes{Colors.ENDC}")
        print(f"3. {Colors.CYAN}View Notes by Category{Colors.ENDC}")
        print(f"4. {Colors.CYAN}Search Notes{Colors.ENDC}")
        print(f"5. {Colors.CYAN}Delete Note{Colors.ENDC}")
        print(f"6. {Colors.CYAN}Exit{Colors.ENDC}")
        
        choice = input(f"{Colors.BOLD}\nEnter your choice (1-6): {Colors.ENDC}")

        if choice == '1':
            title = input(f"{Colors.BOLD}Enter note title: {Colors.ENDC}")
            content = input(f"{Colors.BOLD}Enter note content: {Colors.ENDC}")
            organizer.add_note(title, content)
            time.sleep(1)
        elif choice == '2':
            organizer.view_notes()
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        elif choice == '3':
            category = input(f"{Colors.BOLD}Enter category to filter by (e.g., Work, Study, Personal): {Colors.ENDC}")
            organizer.view_notes(category)
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        elif choice == '4':
            query = input(f"{Colors.BOLD}Enter a search keyword: {Colors.ENDC}")
            organizer.search_notes(query)
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
        elif choice == '5':
            try:
                note_id = int(input(f"{Colors.BOLD}Enter ID of the note to delete: {Colors.ENDC}"))
                organizer.delete_note(note_id)
            except ValueError:
                print(f"{Colors.FAIL}Invalid ID. Please enter a number.{Colors.ENDC}")
            time.sleep(1)
        elif choice == '6':
            print(f"{Colors.GREEN}Thank you for using the Note Organizer!{Colors.ENDC}")
            break
        else:
            print(f"{Colors.FAIL}Invalid choice. Please try again.{Colors.ENDC}")
            time.sleep(1)

if __name__ == "__main__":
    main()