from typing import List, Optional


def handle_help_command(args: Optional[List[str]]) -> None:
    if not args:
        print("""
            Available help topics:
            drive   - Upload, download, share, and list files on Google Drive
            zip     - Create, add, extract, or remove files from ZIP archives
            pdf     - Split, merge, extract, and search PDF files

            Usage:
            help <topic>
            Example:
            help drive
              """)
        return
    topic = args[0].lower()
    if topic == "drive":
        print("""
            Drive Commands:
            drive init <username>             - Authenticate or initialize a Drive session
            drive logout                       - Remove stored credentials and logout
            drive list                        - List folders and files in your Drive
            drive upload <path> [drive_folder] - Upload a file or all files in a folder
            drive download <drive_item> [dest] - Download a file/folder from Drive
            drive share <item> [email]        - Share a file/folder (public or to a user)

            Examples:
            drive upload report.pdf "Work Docs"
            drive download "MyFolder" downloads/
            drive share report.pdf someone@gmail.com
            """)
    elif topic == "zip":
         print("""
            ZIP Commands:
            zip add <path> <archive_name>     - Add a file or folder to a ZIP archive
                zip list [archive_name]           - Show all registered archives or contents of a specific archive
            zip archives                       - List known zip archives and counts
            zip extract <archive_name> [dest] - Extract all or specific files
            zip remove <archive_name> <file>  - Remove a file from the ZIP

            Examples:
            zip add ./docs my_archive.zip
            zip list my_archive.zip
            zip extract my_archive.zip extracted/
            """)
    elif topic == "pdf":
        print("""
            PDF Commands:
            pdf split <file> <ranges>         - Split a PDF by page ranges (e.g., "1-3,4-6")
            pdf merge <file1> <file2> ...     - Merge multiple PDFs into one
            pdf extract <file> <pages> <new>  - Extract pages to a new PDF
            pdf search <file> <keyword>       - Search for text inside a PDF
            pdf convert <file|dir|file1 file2 ...> [out.pdf] [delete] - Convert files (images/txt/docx) to PDF

            Examples:
            pdf split report.pdf "1-5,6-10"
            pdf merge part1.pdf part2.pdf
            pdf extract book.pdf "10-15" summary.pdf
            pdf search notes.pdf "machine learning"
            pdf convert myfiles/                 # convert all files in folder
            pdf convert a.txt b.txt out.pdf     # convert two files and combine into out.pdf
            """)
    else:
        print(f"No help available for '{topic}'.")