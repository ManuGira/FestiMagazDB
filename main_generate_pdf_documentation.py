import os
import subprocess
from pypdf import PdfReader

DOC_FOLDER = "./doc"
TMP_FOLDER = "./.tmp"
OUTPUT_FILE = "./FestiMagazDB documentation.pdf"


def check_pandoc_installed():
    """Check if Pandoc is available in the system."""
    from shutil import which
    if which("pandoc") is None:
        raise EnvironmentError("Pandoc is not installed or not found in PATH.")


def list_markdown_files(folder):
    """Return a sorted list of .md files in the given folder."""
    return sorted([
        f for f in os.listdir(folder)
        if f.endswith(".md")
    ])


def generate_pdf(source_md_path, output_pdf_path, resource_path):
    """Generate a PDF from a Markdown file using Pandoc."""
    cmd = [
        "pandoc",
        source_md_path,
        "-o", output_pdf_path,
        f"--resource-path={resource_path}"
    ]
    subprocess.run(cmd, check=True)


def get_pdf_page_count(pdf_file_path):
    """Return the number of pages in a PDF file."""
    reader = PdfReader(pdf_file_path)
    return len(reader.pages)


def insert_newpages_in_markdown(original_md_path, num_blank_pages):
    """Append \\newpage commands at the end of the Markdown file."""
    with open(original_md_path, "a", encoding="utf-8") as f:
        for _ in range(num_blank_pages):
            f.write("  \n\\newpage\n  ")


def prepare_markdown_files(folder, temp_folder):
    """
    For each .md file:
    - Generate a temporary PDF
    - Count its pages
    - If page count is odd, add 1 \newpage
    - Return final list of markdown file paths (in order)
    """
    md_files = list_markdown_files(folder)
    final_md_paths = []

    os.makedirs(temp_folder, exist_ok=True)

    print("Checking page counts for each Markdown file...")

    for md_file in md_files:
        md_path = os.path.join(folder, md_file)
        pdf_path = os.path.join(temp_folder, f"{os.path.splitext(md_file)[0]}.pdf")

        # Copy original file to reset any previous \newpage edits
        tmp_md_path = os.path.join(temp_folder, md_file)
        with open(md_path, "r", encoding="utf-8") as src, open(tmp_md_path, "w", encoding="utf-8") as dst:
            dst.write(src.read())

        # Generate PDF from the copied version
        generate_pdf(tmp_md_path, pdf_path, folder)

        # Count pages
        page_count = get_pdf_page_count(pdf_path)
        print(f"{md_file} -> {page_count} page(s)")

        # Add page breaks to have even number of pages
        page_break_to_add = 1 if (page_count % 2 == 0) else 2
        insert_newpages_in_markdown(tmp_md_path, page_break_to_add)

        final_md_paths.append(tmp_md_path)

    return final_md_paths


def merge_all_markdown_to_pdf(markdown_files, output_pdf, resource_path):
    """Combine all Markdown files into one final PDF with consistent pagination."""
    cmd = [
        "pandoc",
        *markdown_files,
        "-o", output_pdf,
        f"--resource-path={resource_path}"
    ]
    subprocess.run(cmd, check=True)


def main():
    check_pandoc_installed()

    os.makedirs(TMP_FOLDER, exist_ok=True)

    # Step 1: Prepare each Markdown file (PDF generation + page check)
    markdown_with_padding = prepare_markdown_files(DOC_FOLDER, TMP_FOLDER)

    # Step 2: Combine everything into one final PDF
    print("Generating final PDF...")
    merge_all_markdown_to_pdf(markdown_with_padding, OUTPUT_FILE, DOC_FOLDER)

    print(f"Final PDF generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
