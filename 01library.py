#!/usr/bin/env python3
"""
01LIBRARY - Interactive E-book Library Manager
A CLI application for managing your e-book collection with lists and symlinks

Author: PedramBHT
Version: 1.0.0
License: MIT License

Copyright (c) 2025 PedramBHT

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

GitHub: https://github.com/pedram_bht/01library
Email: [pbhtash@email.com]
"""

import os
import json
import shutil
import subprocess
import platform
from pathlib import Path
from datetime import datetime
import sys

class EbookLibrary:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.books_dir = self.base_dir / "books"
        self.database_dir = self.base_dir / "database"
        self.db_file = self.database_dir / "library.json"
        self.current_list = "default"
        
        # Initialize directories and database
        self.setup_directories()
        self.load_database()
    
    def setup_directories(self):
        """Create necessary directories if they don't exist"""
        self.books_dir.mkdir(exist_ok=True)
        self.database_dir.mkdir(exist_ok=True)
        
        # Create lists subdirectories in books
        (self.books_dir / "default").mkdir(exist_ok=True)
    
    def load_database(self):
        """Load or create the database"""
        if self.db_file.exists():
            try:
                with open(self.db_file, 'r') as f:
                    self.database = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.database = {"lists": {"default": {}}, "current_list": "default"}
        else:
            self.database = {"lists": {"default": {}}, "current_list": "default"}
        
        self.current_list = self.database.get("current_list", "default")
    
    def save_database(self):
        """Save database to file"""
        self.database["current_list"] = self.current_list
        with open(self.db_file, 'w') as f:
            json.dump(self.database, f, indent=2)
    
    def display_ascii_art(self):
        """Display the ASCII art logo"""
        ascii_art = """
╔═════════════════════════════════════════════════════════════════════════╗
║   ░█████╗░░███╗░░██╗░░░░░██╗██████╗░██████╗░░█████╗░██████╗░██╗░░░██╗   ║
║   ██╔══██╗░███║░░██║░░░░░██║██╔══██╗██╔══██╗██╔══██╗██╔══██╗╚██╗░██╔╝   ║
║   ██║░░██║░╚██║░░██║░░░░░██║██████╦╝██████╔╝███████║██████╔╝░╚████╔╝░   ║
║   ██║░░██║░░██║░░██║░░░░░██║██╔══██╗██╔══██╗██╔══██║██╔══██╗░░╚██╔╝░░   ║
║   ╚█████╔╝░░██║░░███████╗██║██████╦╝██║░░██║██║░░██║██║░░██║░░░██║░░░   ║
║   ░╚════╝░░░╚═╝░░╚══════╝╚═╝╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░   ║
║                                                                         ║
║                    📚 Your Personal E-book Library 📚                   ║
║                            Author: PedramBHT                            ║
║                              Licence: MIT                               ║
║                             Version : 1.0.0                             ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
        """
        print(ascii_art)
        print(f"Current List: 📁 {self.current_list}")
        print("═" * 75)
    
    def display_menu(self):
        """Display the main menu"""
        menu = """
🔹 MAIN MENU 🔹
1. 📖 Add Book
2. 🗑️  Delete Book
3. 📋 Add List
4. 🗂️  Delete List
5. 📚 Switch Lists
6. 📜 Show All Books
7. 📂 Open Book
8. 🚪 Exit

Choose an option (1-8): """
        return input(menu).strip()
    
    def add_book(self):
        """Add a new book to the current list"""
        print(f"\n📖 Adding book to list: '{self.current_list}'")
        book_path = input("Enter the full path to the book file: ").strip()
        
        if not book_path:
            print("❌ No path provided!")
            return
        
        book_path = Path(book_path)
        
        if not book_path.exists():
            print("❌ File doesn't exist!")
            return
        
        if not book_path.is_file():
            print("❌ Path is not a file!")
            return
        
        # Get book info
        book_name = book_path.name
        book_size = self.format_size(book_path.stat().st_size)
        
        # Create list directory if it doesn't exist
        list_dir = self.books_dir / self.current_list
        list_dir.mkdir(exist_ok=True)
        
        # Create symlink
        symlink_path = list_dir / book_name
        
        # Handle duplicate names
        counter = 1
        original_name = book_path.stem
        extension = book_path.suffix
        
        while symlink_path.exists():
            new_name = f"{original_name}_{counter}{extension}"
            symlink_path = list_dir / new_name
            counter += 1
        
        try:
            # Create symlink
            if os.name == 'nt':  # Windows
                shutil.copy2(book_path, symlink_path)
                print("📝 Note: Created copy instead of symlink (Windows)")
            else:  # Unix/Linux/Mac
                os.symlink(book_path.absolute(), symlink_path)
            
            # Add to database
            if self.current_list not in self.database["lists"]:
                self.database["lists"][self.current_list] = {}
            
            self.database["lists"][self.current_list][symlink_path.name] = {
                "name": symlink_path.name,
                "size": book_size,
                "location": str(book_path.absolute()),
                "added_date": datetime.now().isoformat()
            }
            
            self.save_database()
            print(f"✅ Successfully added '{symlink_path.name}' ({book_size})")
            
        except Exception as e:
            print(f"❌ Error adding book: {e}")
    
    def delete_book(self):
        """Delete a book from the current list"""
        books = self.database["lists"].get(self.current_list, {})
        
        if not books:
            print(f"📭 No books in list '{self.current_list}'")
            return
        
        print(f"\n🗑️ Delete book from '{self.current_list}':")
        book_names = list(books.keys())
        
        for i, book_name in enumerate(book_names, 1):
            book_info = books[book_name]
            print(f"{i}. {book_info['name']} ({book_info['size']})")
        
        try:
            choice = int(input(f"\nSelect book to delete (1-{len(book_names)}): "))
            if 1 <= choice <= len(book_names):
                book_name = book_names[choice - 1]
                
                # Remove symlink
                symlink_path = self.books_dir / self.current_list / book_name
                if symlink_path.exists():
                    symlink_path.unlink()
                
                # Remove from database
                del self.database["lists"][self.current_list][book_name]
                self.save_database()
                
                print(f"✅ Deleted '{book_name}'")
            else:
                print("❌ Invalid selection!")
        except ValueError:
            print("❌ Please enter a number!")
    
    def add_list(self):
        """Add a new list"""
        list_name = input("\n📋 Enter new list name: ").strip()
        
        if not list_name:
            print("❌ List name cannot be empty!")
            return
        
        if list_name in self.database["lists"]:
            print(f"❌ List '{list_name}' already exists!")
            return
        
        # Create list directory
        list_dir = self.books_dir / list_name
        list_dir.mkdir(exist_ok=True)
        
        # Add to database
        self.database["lists"][list_name] = {}
        self.save_database()
        
        print(f"✅ Created list '{list_name}'")
    
    def delete_list(self):
        """Delete a list"""
        lists = list(self.database["lists"].keys())
        
        if len(lists) <= 1:
            print("❌ Cannot delete the last remaining list!")
            return
        
        print("\n🗂️ Available lists:")
        for i, list_name in enumerate(lists, 1):
            book_count = len(self.database["lists"][list_name])
            print(f"{i}. {list_name} ({book_count} books)")
        
        try:
            choice = int(input(f"\nSelect list to delete (1-{len(lists)}): "))
            if 1 <= choice <= len(lists):
                list_name = lists[choice - 1]
                
                if list_name == self.current_list:
                    print("❌ Cannot delete the current active list!")
                    return
                
                # Remove directory and all symlinks
                list_dir = self.books_dir / list_name
                if list_dir.exists():
                    shutil.rmtree(list_dir)
                
                # Remove from database
                del self.database["lists"][list_name]
                self.save_database()
                
                print(f"✅ Deleted list '{list_name}'")
            else:
                print("❌ Invalid selection!")
        except ValueError:
            print("❌ Please enter a number!")
    
    def switch_lists(self):
        """Switch between lists"""
        lists = list(self.database["lists"].keys())
        
        if len(lists) == 1:
            print(f"📋 Only one list available: '{lists[0]}'")
            return
        
        print("\n📚 Available lists:")
        for i, list_name in enumerate(lists, 1):
            book_count = len(self.database["lists"][list_name])
            current = " (current)" if list_name == self.current_list else ""
            print(f"{i}. {list_name} ({book_count} books){current}")
        
        try:
            choice = int(input(f"\nSelect list to switch to (1-{len(lists)}): "))
            if 1 <= choice <= len(lists):
                self.current_list = lists[choice - 1]
                self.save_database()
                print(f"✅ Switched to list '{self.current_list}'")
            else:
                print("❌ Invalid selection!")
        except ValueError:
            print("❌ Please enter a number!")
    
    def show_all_books(self):
        """Show all books in current list"""
        books = self.database["lists"].get(self.current_list, {})
        
        if not books:
            print(f"📭 No books in list '{self.current_list}'")
            return
        
        print(f"\n📜 Books in '{self.current_list}':")
        print("═" * 60)
        
        for i, (book_name, book_info) in enumerate(books.items(), 1):
            print(f"{i:2d}. 📖 {book_info['name']}")
            print(f"     📏 Size: {book_info['size']}")
            print(f"     📍 Location: {book_info['location']}")
            if 'added_date' in book_info:
                date_added = datetime.fromisoformat(book_info['added_date']).strftime("%Y-%m-%d %H:%M")
                print(f"     📅 Added: {date_added}")
            print()
    
    @staticmethod
    def format_size(size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
    
    
    def open_book(self):
        """Open a selected book with the default system application"""
        books = self.database["lists"].get(self.current_list, {})
        
        if not books:
            print(f"📭 No books in list '{self.current_list}'")
            return
        
        print(f"\n📂 Open book from '{self.current_list}':")
        book_names = list(books.keys())
        
        for i, book_name in enumerate(book_names, 1):
            book_info = books[book_name]
            print(f"{i}. {book_info['name']} ({book_info['size']})")
        
        try:
            choice = int(input(f"\nSelect book to open (1-{len(book_names)}): "))
            if 1 <= choice <= len(book_names):
                book_name = book_names[choice - 1]
                book_info = books[book_name]
                
                # Try to open the original file first, then the symlink
                original_path = Path(book_info['location'])
                symlink_path = self.books_dir / self.current_list / book_name
                
                file_to_open = None
                if original_path.exists():
                    file_to_open = original_path
                elif symlink_path.exists():
                    file_to_open = symlink_path
                else:
                    print(f"❌ Book file not found! Original: {original_path}")
                    print("The file may have been moved or deleted.")
                    return
                
                print(f"📂 Opening '{book_info['name']}'...")
                
                try:
                    # Cross-platform file opening
                    system = platform.system()
                    if system == "Windows":
                        os.startfile(str(file_to_open))
                    elif system == "Darwin":  # macOS
                        subprocess.run(["open", str(file_to_open)], check=True)
                    else:  # Linux and other Unix-like systems
                        subprocess.run(["xdg-open", str(file_to_open)], check=True)
                    
                    print("✅ Book opened successfully!")
                    
                except subprocess.CalledProcessError:
                    print("❌ Failed to open the book. No default application found.")
                except Exception as e:
                    print(f"❌ Error opening book: {e}")
                    print("You can manually open the file at:")
                    print(f"📍 {file_to_open}")
            else:
                print("❌ Invalid selection!")
        except ValueError:
            print("❌ Please enter a number!")
    
    
    def run(self):
        """Main application loop"""
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')  # Clear screen
            self.display_ascii_art()
            
            choice = self.display_menu()
            
            if choice == '1':
                self.add_book()
            elif choice == '2':
                self.delete_book()
            elif choice == '3':
                self.add_list()
            elif choice == '4':
                self.delete_list()
            elif choice == '5':
                self.switch_lists()
            elif choice == '6':
                self.show_all_books()
            elif choice == '7':
                self.open_book()
            elif choice == '8':
                print("\n" + "═" * 75)
                print("👋 Thank you for using 01LIBRARY!")
                print("📧 For support or feedback: [your-email@example.com]")
                print("🌟 Star us on GitHub: https://github.com/[your-username]/01library")
                print("📄 Licensed under MIT - Free and Open Source!")
                print("═" * 75)
                break
            else:
                print("❌ Invalid option! Please choose 1-8.")
            
            if choice != '8':
                input("\nPress Enter to continue...")

def main():
    """Main entry point"""
    try:
        library = EbookLibrary()
        library.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
