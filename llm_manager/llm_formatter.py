"""Format command documentation into structured JSON for LLM context."""

import json
from typing import Dict, Any


def get_command_schema() -> Dict[str, Any]:
    """Return structured schema of all available commands for LLM context.
    
    This provides the LLM with a complete understanding of what commands
    the application supports, their syntax, and usage.
    """
    schema = {
        "app_name": "pdfkitx",
        "description": "PDF, ZIP, and Google Drive CLI toolkit",
        "commands": {
            "pdf": {
                "description": "PDF file manipulation and analysis",
                "subcommands": [
                    {
                        "name": "split",
                        "syntax": "pdf split <file> <ranges>",
                        "description": "Split a PDF by page ranges",
                        "examples": [
                            "pdf split report.pdf \"1-3,4-6\"",
                            "pdf split document.pdf \"1-5\"",
                            "pdf split file.pdf \"2,4,6-10\""
                        ],
                        "parameters": [
                            {
                                "name": "file",
                                "type": "path",
                                "description": "Path to the PDF file"
                            },
                            {
                                "name": "ranges",
                                "type": "string",
                                "description": "Page ranges (e.g., '1-3,5,7-10')"
                            }
                        ]
                    },
                    {
                        "name": "merge",
                        "syntax": "pdf merge <file1> <file2> ... --out <output>",
                        "description": "Merge multiple PDF files into one",
                        "examples": [
                            "pdf merge part1.pdf part2.pdf --out merged.pdf",
                            "pdf merge a.pdf b.pdf c.pdf --out combined.pdf"
                        ],
                        "parameters": [
                            {
                                "name": "files",
                                "type": "path[]",
                                "description": "Two or more PDF files to merge"
                            },
                            {
                                "name": "out",
                                "type": "path",
                                "description": "Output file path for merged PDF"
                            }
                        ]
                    },
                    {
                        "name": "extract",
                        "syntax": "pdf extract <file> <pages> <output>",
                        "description": "Extract specific pages to a new PDF",
                        "examples": [
                            "pdf extract book.pdf \"10-15\" summary.pdf",
                            "pdf extract document.pdf \"1,5,10\" extracted.pdf"
                        ],
                        "parameters": [
                            {
                                "name": "file",
                                "type": "path",
                                "description": "Source PDF file"
                            },
                            {
                                "name": "pages",
                                "type": "string",
                                "description": "Pages to extract (e.g., '1-5' or '1,3,5')"
                            },
                            {
                                "name": "output",
                                "type": "path",
                                "description": "Output PDF file path"
                            }
                        ]
                    },
                    {
                        "name": "search",
                        "syntax": "pdf search <file> <keyword>",
                        "description": "Search for text inside a PDF",
                        "examples": [
                            "pdf search notes.pdf \"machine learning\"",
                            "pdf search document.pdf \"conclusion\""
                        ],
                        "parameters": [
                            {
                                "name": "file",
                                "type": "path",
                                "description": "PDF file to search"
                            },
                            {
                                "name": "keyword",
                                "type": "string",
                                "description": "Text to search for"
                            }
                        ]
                    },
                    {
                        "name": "convert",
                        "syntax": "pdf convert <input_files> [output] [delete]",
                        "description": "Convert files (images/txt/docx) to PDF",
                        "examples": [
                            "pdf convert myfiles/",
                            "pdf convert a.txt b.txt out.pdf",
                            "pdf convert image.jpg converted.pdf"
                        ],
                        "parameters": [
                            {
                                "name": "input_files",
                                "type": "path|path[]",
                                "description": "File or directory to convert"
                            },
                            {
                                "name": "output",
                                "type": "path",
                                "description": "Output PDF file path (optional)"
                            }
                        ]
                    }
                ]
            },
            "zip": {
                "description": "ZIP archive creation and management",
                "subcommands": [
                    {
                        "name": "add",
                        "syntax": "zip add <path> <archive_name>",
                        "description": "Add a file or folder to a ZIP archive",
                        "examples": [
                            "zip add ./docs my_archive.zip",
                            "zip add report.pdf archive.zip"
                        ],
                        "parameters": [
                            {
                                "name": "path",
                                "type": "path",
                                "description": "File or folder to add"
                            },
                            {
                                "name": "archive_name",
                                "type": "string",
                                "description": "Name of the ZIP archive"
                            }
                        ]
                    },
                    {
                        "name": "list",
                        "syntax": "zip list [archive_name]",
                        "description": "Show contents of a ZIP archive",
                        "examples": [
                            "zip list my_archive.zip",
                            "zip list"
                        ],
                        "parameters": [
                            {
                                "name": "archive_name",
                                "type": "string",
                                "description": "Archive name (optional)"
                            }
                        ]
                    },
                    {
                        "name": "extract",
                        "syntax": "zip extract <archive_name> [dest]",
                        "description": "Extract files from a ZIP archive",
                        "examples": [
                            "zip extract my_archive.zip extracted/",
                            "zip extract my_archive.zip"
                        ],
                        "parameters": [
                            {
                                "name": "archive_name",
                                "type": "string",
                                "description": "Archive to extract"
                            },
                            {
                                "name": "dest",
                                "type": "path",
                                "description": "Destination folder (optional)"
                            }
                        ]
                    },
                    {
                        "name": "remove",
                        "syntax": "zip remove <archive_name> <file>",
                        "description": "Remove a file from a ZIP archive",
                        "examples": [
                            "zip remove my_archive.zip old_file.txt"
                        ],
                        "parameters": [
                            {
                                "name": "archive_name",
                                "type": "string",
                                "description": "Archive name"
                            },
                            {
                                "name": "file",
                                "type": "string",
                                "description": "File to remove"
                            }
                        ]
                    }
                ]
            },
            "drive": {
                "description": "Google Drive integration (requires BYOC setup)",
                "requires_auth": True,
                "subcommands": [
                    {
                        "name": "init",
                        "syntax": "drive init [username]",
                        "description": "Authenticate or initialize a Drive session",
                        "examples": [
                            "drive init myname",
                            "drive init"
                        ],
                        "parameters": [
                            {
                                "name": "username",
                                "type": "string",
                                "description": "Optional username to store"
                            }
                        ]
                    },
                    {
                        "name": "logout",
                        "syntax": "drive logout",
                        "description": "Remove stored credentials and logout",
                        "examples": [
                            "drive logout"
                        ],
                        "parameters": []
                    },
                    {
                        "name": "list",
                        "syntax": "drive list",
                        "description": "List folders and files in your Drive",
                        "examples": [
                            "drive list"
                        ],
                        "parameters": []
                    },
                    {
                        "name": "upload",
                        "syntax": "drive upload <path> [drive_folder]",
                        "description": "Upload a file or folder to Google Drive",
                        "examples": [
                            "drive upload report.pdf \"Work Docs\"",
                            "drive upload ./files/ backup"
                        ],
                        "parameters": [
                            {
                                "name": "path",
                                "type": "path",
                                "description": "Local file or folder to upload"
                            },
                            {
                                "name": "drive_folder",
                                "type": "string",
                                "description": "Drive folder name (optional)"
                            }
                        ]
                    },
                    {
                        "name": "download",
                        "syntax": "drive download <file_name> [destination]",
                        "description": "Download a file from Google Drive",
                        "examples": [
                            "drive download \"MyDocument\" downloads/",
                            "drive download important.pdf"
                        ],
                        "parameters": [
                            {
                                "name": "file_name",
                                "type": "string",
                                "description": "Name of file in Drive"
                            },
                            {
                                "name": "destination",
                                "type": "path",
                                "description": "Destination folder (optional)"
                            }
                        ]
                    },
                    {
                        "name": "share",
                        "syntax": "drive share <item> [email]",
                        "description": "Share a file/folder (public or to specific email)",
                        "examples": [
                            "drive share report.pdf someone@gmail.com",
                            "drive share report.pdf"
                        ],
                        "parameters": [
                            {
                                "name": "item",
                                "type": "string",
                                "description": "File or folder name"
                            },
                            {
                                "name": "email",
                                "type": "string",
                                "description": "Email address (optional, default is public)"
                            }
                        ]
                    }
                ]
            }
        },
        "notes": {
            "syntax": "All commands use space-separated arguments. Paths with spaces should be quoted.",
            "drive_requires_auth": "Drive commands require credentials.json setup (BYOC model)",
            "pdf_zip_always_available": "PDF and ZIP commands work without any authentication"
        }
    }
    return schema


def get_command_schema_json() -> str:
    """Return command schema as formatted JSON string for LLM."""
    return json.dumps(get_command_schema(), indent=2)
