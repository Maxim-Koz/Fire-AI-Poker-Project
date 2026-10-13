import os
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.formatters import ImageFormatter

project_dir = "."
output_dir = "code_images"

exclude_dirs = {".git", "__pycache__", "node_modules", "venv", ".venv"}
include_extensions = {".py", ".java", ".js", ".cpp", ".c", ".html", ".css", ".json"}

lines_per_image = 40  # adjust to fit Word pages
font_size = 16  # fixed font size for all images

os.makedirs(output_dir, exist_ok=True)

for root, dirs, files in os.walk(project_dir):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]

    for file in files:
        ext = os.path.splitext(file)[1]
        if ext not in include_extensions:
            continue

        path = os.path.join(root, file)

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        lexer = guess_lexer_for_filename(file, "".join(lines))

        # split file into chunks
        for i in range(0, len(lines), lines_per_image):
            chunk = "".join(lines[i : i + lines_per_image])

            formatter = ImageFormatter(
                font_name="DejaVu Sans Mono",
                font_size=font_size,
                line_numbers=True,
                line_number_start=i + 1,
                style="monokai",
            )

            img = highlight(chunk, lexer, formatter)

            out_file = os.path.join(
                output_dir, f"{file}_part{i // lines_per_image + 1}.png"
            )

            with open(out_file, "wb") as f:
                f.write(img)

            print("Exported:", out_file)
