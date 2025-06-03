#!/usr/bin/env python3
"""
Text to Single String Converter
Converts any text into one long string with \n between paragraphs
"""

import re
import sys

def convert_text_to_single_string(text):
    """
    Convert text to a single string with \n between paragraphs.

    Args:
        text (str): Input text to convert

    Returns:
        str: Single string with \n separating paragraphs
    """
    # Split text into paragraphs (split on double newlines or more)
    paragraphs = re.split(r'\n\s*\n', text.strip())

    # Remove empty paragraphs and strip whitespace from each
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    # For each paragraph, replace internal newlines with spaces
    cleaned_paragraphs = []
    for paragraph in paragraphs:
        # Replace internal newlines and multiple spaces with single spaces
        cleaned = re.sub(r'\s+', ' ', paragraph)
        cleaned_paragraphs.append(cleaned)

    # Join paragraphs with \n
    result = '\\n'.join(cleaned_paragraphs)

    return result

def main():
    """Main function to handle command line usage or interactive input."""

    if len(sys.argv) > 1:
        # If filename provided as argument
        filename = sys.argv[1]
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                text = file.read()
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    else:
        # Interactive input
        print("Enter your text (press Ctrl+D on Unix/Mac or Ctrl+Z on Windows when finished):")
        try:
            text = sys.stdin.read()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return

    # Convert the text
    result = convert_text_to_single_string(text)

    # Output the result
    print("\nConverted text:")
    print(result)

    # Optionally save to file
    save = input("\nSave to file? (y/n): ").lower().strip()
    if save in ['y', 'yes']:
        output_filename = input("Enter output filename: ").strip()
        try:
            with open(output_filename, 'w', encoding='utf-8') as file:
                file.write(result)
            print(f"Saved to '{output_filename}'")
        except Exception as e:
            print(f"Error saving file: {e}")

if __name__ == "__main__":
    # Example usage
    sample_text = """This is the first paragraph.
It has multiple lines
in it.

This is the second paragraph.
It also has multiple lines.


This is the third paragraph.
After some extra spacing."""

    print("Example conversion:")
    print("Original text:")
    print(repr(sample_text))
    print("\nConverted:")
    print(repr(convert_text_to_single_string(sample_text)))
    print("\nActual output:")
    print(convert_text_to_single_string(sample_text))
    print("\n" + "="*50)

    main()