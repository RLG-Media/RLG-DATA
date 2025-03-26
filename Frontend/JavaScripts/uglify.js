// Import necessary modules
const fs = require('fs');
const path = require('path');
const UglifyJS = require('uglify-js');
const glob = require('glob');

// Directory paths for RLG Data and RLG Fans JavaScript files
const RLG_DATA_JS_DIR = path.join(__dirname, 'rlg_data/js');
const RLG_FANS_JS_DIR = path.join(__dirname, 'rlg_fans/js');

// Directory for storing minified and uglified JS files
const OUTPUT_DIR = path.join(__dirname, 'dist/js');

// Create the output directory if it doesn't exist
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// Function to minify and uglify a single JavaScript file
function minifyAndUglify(filePath) {
  try {
    // Read the content of the JavaScript file
    const fileContent = fs.readFileSync(filePath, 'utf8');

    // UglifyJS options to compress and mangle variable names
    const result = UglifyJS.minify(fileContent, {
      compress: {
        drop_console: true,  // Remove all console statements
        passes: 2,  // Perform two passes of compression
      },
      mangle: {
        toplevel: true,  // Mangle top-level variable names
      },
    });

    // Check for errors during minification
    if (result.error) {
      console.error(`Error minifying file: ${filePath}`, result.error);
      return;
    }

    // Generate the output file name
    const outputFileName = path.basename(filePath);
    const outputFilePath = path.join(OUTPUT_DIR, outputFileName);

    // Write the minified and uglified content to the output directory
    fs.writeFileSync(outputFilePath, result.code);
    console.log(`Minified and uglified: ${filePath} -> ${outputFilePath}`);
  } catch (error) {
    console.error(`Error processing file: ${filePath}`, error);
  }
}

// Function to process all JavaScript files in a directory
function processJSFilesInDirectory(directory) {
  // Use glob to match all JavaScript files in the directory (including subdirectories)
  glob(path.join(directory, '**/*.js'), (err, files) => {
    if (err) {
      console.error(`Error reading directory: ${directory}`, err);
      return;
    }

    // Process each JavaScript file
    files.forEach((file) => {
      minifyAndUglify(file);
    });
  });
}

// Process the JavaScript files for both RLG Data and RLG Fans
processJSFilesInDirectory(RLG_DATA_JS_DIR);
processJSFilesInDirectory(RLG_FANS_JS_DIR);

console.log('JavaScript minification and uglification completed.');

const result = UglifyJS.minify(fileContent, {
    compress: {
      drop_console: true,
      passes: 2,
    },
    mangle: {
      toplevel: true,
    },
    sourceMap: {
      filename: path.basename(filePath),
      url: `${path.basename(filePath)}.map`,
    },
  });
  
  const chokidar = require('chokidar');

// Watch JavaScript files for changes
chokidar.watch([RLG_DATA_JS_DIR, RLG_FANS_JS_DIR], { ignored: /node_modules/ })
  .on('change', (filePath) => {
    console.log(`${filePath} changed, minifying...`);
    minifyAndUglify(filePath);
  });
