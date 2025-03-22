import os
import logging
import subprocess
from pathlib import Path
from glob import glob
from pathlib import Path
from cssmin import cssmin
from jsmin import jsmin
import htmlmin
import shutil

# Initialize logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Directory paths for source and output
SRC_DIR = Path("assets")  # Directory containing the source JS, CSS, HTML files
OUTPUT_DIR = Path("dist")  # Output directory for minified and bundled files
if not OUTPUT_DIR.exists():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Configuration for minification and bundling
CONFIG = {
    "js_files": glob(str(SRC_DIR / "**/*.js"), recursive=True),  # List of JavaScript files
    "css_files": glob(str(SRC_DIR / "**/*.css"), recursive=True),  # List of CSS files
    "html_files": glob(str(SRC_DIR / "**/*.html"), recursive=True),  # List of HTML files
    "bundle_js": True,  # Whether to bundle JS files into a single file
    "bundle_css": True,  # Whether to bundle CSS files into a single file
    "minify_html": True,  # Whether to minify HTML files
}

def minify_js(js_file: Path) -> str:
    """Minify JavaScript files."""
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    minified_content = jsmin(content)
    return minified_content

def minify_css(css_file: Path) -> str:
    """Minify CSS files."""
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    minified_content = cssmin(content)
    return minified_content

def minify_html(html_file: Path) -> str:
    """Minify HTML files."""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    minified_content = htmlmin.minify(content, remove_empty_space=True)
    return minified_content

def bundle_files(file_list: list, output_filename: str, is_js: bool = False) -> str:
    """Bundle multiple files into one."""
    bundled_content = ""
    for file in file_list:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        if is_js:
            # JavaScript files may require a small header for closure or initializations
            bundled_content += f"\n// File: {file}\n" + content + "\n"
        else:
            bundled_content += f"\n/* File: {file} */\n" + content + "\n"
    return bundled_content

def write_to_file(output_dir: Path, filename: str, content: str) -> None:
    """Write minified or bundled content to a new file."""
    output_file = output_dir / filename
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"Written to {output_file}")

def process_js_files() -> None:
    """Process JavaScript files: minify and bundle if needed."""
    js_output_file = OUTPUT_DIR / "bundle.js"
    if CONFIG["bundle_js"]:
        # Bundle JS files
        logger.info("Bundling JavaScript files...")
        bundled_js = bundle_files(CONFIG["js_files"], "bundle.js", is_js=True)
        minified_js = minify_js(bundled_js)
        write_to_file(OUTPUT_DIR, "bundle.min.js", minified_js)
    else:
        # Minify individual JS files
        logger.info("Minifying JavaScript files...")
        for js_file in CONFIG["js_files"]:
            minified_js = minify_js(Path(js_file))
            output_filename = Path(js_file).name.replace('.js', '.min.js')
            write_to_file(OUTPUT_DIR, output_filename, minified_js)

def process_css_files() -> None:
    """Process CSS files: minify and bundle if needed."""
    css_output_file = OUTPUT_DIR / "bundle.css"
    if CONFIG["bundle_css"]:
        # Bundle CSS files
        logger.info("Bundling CSS files...")
        bundled_css = bundle_files(CONFIG["css_files"], "bundle.css", is_js=False)
        minified_css = minify_css(bundled_css)
        write_to_file(OUTPUT_DIR, "bundle.min.css", minified_css)
    else:
        # Minify individual CSS files
        logger.info("Minifying CSS files...")
        for css_file in CONFIG["css_files"]:
            minified_css = minify_css(Path(css_file))
            output_filename = Path(css_file).name.replace('.css', '.min.css')
            write_to_file(OUTPUT_DIR, output_filename, minified_css)

def process_html_files() -> None:
    """Process HTML files: minify."""
    if CONFIG["minify_html"]:
        logger.info("Minifying HTML files...")
        for html_file in CONFIG["html_files"]:
            minified_html = minify_html(Path(html_file))
            output_filename = Path(html_file).name
            write_to_file(OUTPUT_DIR, output_filename.replace('.html', '.min.html'), minified_html)

def clean_up_previous_build() -> None:
    """Remove old minified/bundled files if any."""
    if OUTPUT_DIR.exists():
        for file in OUTPUT_DIR.glob('*'):
            file.unlink()
        logger.info(f"Cleaned up previous build files in {OUTPUT_DIR}")

def run_minification_and_bundling() -> None:
    """Main function to process the assets."""
    clean_up_previous_build()
    
    process_js_files()
    process_css_files()
    process_html_files()

    logger.info("Minification and Bundling completed.")

if __name__ == "__main__":
    run_minification_and_bundling()
