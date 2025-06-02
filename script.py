import re
import random
import sys

class ColorHighlighter:
    def __init__(self):
        # Available colors for highlighting
        self.highlight_colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'brown', 'white', 'black']

        # Color names to find in text (including variations)
        self.color_words = [
            'red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'brown', 'white', 'black',
            'silver', 'gold', 'golden', 'crimson', 'scarlet', 'amber', 'lime', 'emerald', 'jade',
            'sapphire', 'cobalt', 'navy', 'violet', 'magenta', 'rose', 'coral', 'turquoise',
            'cyan', 'maroon', 'burgundy', 'olive', 'khaki', 'tan', 'beige', 'ivory', 'gray', 'grey'
        ]

        # ANSI color codes for terminal output
        self.ansi_colors = {
            'red': '\033[41m',
            'orange': '\033[48;5;208m',
            'yellow': '\033[43m',
            'green': '\033[42m',
            'blue': '\033[44m',
            'purple': '\033[45m',
            'pink': '\033[48;5;213m',
            'brown': '\033[48;5;94m',
            'white': '\033[47m\033[30m',  # White background with black text
            'black': '\033[40m\033[37m'   # Black background with white text
        }

        self.reset_color = '\033[0m'

    def highlight_terminal(self, text):
        """Highlight color words for terminal display"""
        def replace_color_word(match):
            word = match.group(0)
            highlight_color = random.choice(self.highlight_colors)
            return f"{self.ansi_colors[highlight_color]}{word}{self.reset_color}"

        pattern = r'\b(?:' + '|'.join(self.color_words) + r')\b'
        return re.sub(pattern, replace_color_word, text, flags=re.IGNORECASE)

    def highlight_html(self, text, title="Colorful Text"):
        """Generate HTML with highlighted color words"""
        def replace_color_word(match):
            word = match.group(0)
            highlight_color = random.choice(self.highlight_colors)
            text_color = "black" if highlight_color in ["white", "yellow"] else "white"
            return f'<span style="background-color: {highlight_color}; color: {text_color}; padding: 2px 4px; border-radius: 3px; font-weight: bold;">{word}</span>'

        pattern = r'\b(?:' + '|'.join(self.color_words) + r')\b'
        highlighted_text = re.sub(pattern, replace_color_word, text, flags=re.IGNORECASE)

        # Convert newlines to HTML breaks, preserving paragraph structure
        highlighted_text = highlighted_text.replace('\n\n', '</p><p>').replace('\n', '<br>')

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Georgia', serif;
            line-height: 1.8;
            margin: 40px auto;
            max-width: 800px;
            background-color: #f9f9f9;
            padding: 20px;
        }}
        h1 {{
            color: #333;
            text-align: center;
            border-bottom: 2px solid #ccc;
            padding-bottom: 10px;
        }}
        p {{
            text-align: justify;
            margin-bottom: 15px;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p>{highlighted_text}</p>
    </div>
</body>
</html>"""
        return html_content

def read_file(filename):
    """Read text from a file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def save_html_file(content, filename):
    """Save HTML content to a file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"HTML file saved as '{filename}'")
    except Exception as e:
        print(f"Error saving HTML file: {e}")

def main():
    highlighter = ColorHighlighter()

    print("=== Universal Color Text Highlighter ===\n")
    print("Choose an option:")
    print("1. Enter text directly")
    print("2. Read from a file")
    print("3. Use sample text")

    choice = input("\nEnter your choice (1/2/3): ").strip()

    if choice == '1':
        print("\nEnter your text (press Ctrl+D on Unix/Mac or Ctrl+Z on Windows when finished):")
        try:
            text = sys.stdin.read()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return
        title = input("Enter a title for the HTML file (optional): ").strip() or "Custom Colorful Text"

    elif choice == '2':
        filename = input("Enter the filename: ").strip()
        text = read_file(filename)
        if text is None:
            return
        title = input("Enter a title for the HTML file (optional): ").strip() or f"Colorful {filename}"

    elif choice == '3':
        # Use the original sample text
        text = """The green wizard stepped carefully through the purple forest, his red hat gleaming in the yellow sunlight that filtered through the orange leaves above. His blue robes rustled softly as he navigated around the white mushrooms that dotted the brown forest floor. In his hand, he carried a silver staff topped with a glowing red crystal.

As he walked deeper into the yellow woods, the green moss beneath his feet grew thicker and softer. Orange butterflies danced around his blue beard, while purple flowers bloomed along the winding path. The red cardinal perched on a white birch tree sang a melodious tune, and the wizard's green eyes sparkled with wonder at the beauty surrounding him."""
        title = "Sample Magical Adventure"

    else:
        print("Invalid choice. Exiting.")
        return

    if not text.strip():
        print("No text provided. Exiting.")
        return

    # Display options
    print("\nOutput options:")
    print("1. Terminal display only")
    print("2. HTML file only")
    print("3. Both terminal and HTML")

    output_choice = input("Enter your choice (1/2/3): ").strip()

    if output_choice in ['1', '3']:
        print("\n" + "="*60)
        print("TERMINAL OUTPUT:")
        print("="*60)
        print(highlighter.highlight_terminal(text))
        print("="*60)

    if output_choice in ['2', '3']:
        html_filename = input("\nEnter HTML filename (default: colorful_text.html): ").strip()
        if not html_filename:
            html_filename = "colorful_text.html"

        if not html_filename.endswith('.html'):
            html_filename += '.html'

        html_content = highlighter.highlight_html(text, title)
        save_html_file(html_content, html_filename)

    print(f"\nFound and highlighted {len(re.findall(r'\\b(?:' + '|'.join(highlighter.color_words) + r')\\b', text, re.IGNORECASE))} color words!")

if __name__ == "__main__":
    main()
