const fs = require('fs');
const path = require('path');
const express = require('express');
const multer = require('multer');
const sharp = require('sharp');
const router = express.Router();

const STORAGE_PATH = path.join(__dirname, 'branding_assets');
fs.mkdirSync(STORAGE_PATH, { recursive: true });

const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

const ensureUserDirectory = (userId) => {
    const userDir = path.join(STORAGE_PATH, userId);
    fs.mkdirSync(userDir, { recursive: true });
    return userDir;
};

router.post('/upload-logo/:userId', upload.single('logo'), async (req, res) => {
    try {
        const userId = req.params.userId;
        if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

        const userDir = ensureUserDirectory(userId);
        const filePath = path.join(userDir, 'logo.png');

        await sharp(req.file.buffer)
            .resize({ width: 1024, height: 1024, fit: 'inside' })
            .toFormat('png')
            .toFile(filePath);

        res.json({ message: 'Logo uploaded successfully', filePath });
    } catch (error) {
        res.status(500).json({ error: 'Failed to upload logo' });
    }
});

router.post('/set-color-scheme/:userId', (req, res) => {
    try {
        const userId = req.params.userId;
        const userDir = ensureUserDirectory(userId);
        const filePath = path.join(userDir, 'color_scheme.json');

        fs.writeFileSync(filePath, JSON.stringify(req.body, null, 4));
        res.json({ message: 'Color scheme saved successfully' });
    } catch (error) {
        res.status(500).json({ error: 'Failed to save color scheme' });
    }
});

router.post('/set-font-preferences/:userId', (req, res) => {
    try {
        const userId = req.params.userId;
        const userDir = ensureUserDirectory(userId);
        const filePath = path.join(userDir, 'font_preferences.json');

        fs.writeFileSync(filePath, JSON.stringify(req.body, null, 4));
        res.json({ message: 'Font preferences saved successfully' });
    } catch (error) {
        res.status(500).json({ error: 'Failed to save font preferences' });
    }
});

router.get('/get-branding-settings/:userId', (req, res) => {
    try {
        const userId = req.params.userId;
        const userDir = path.join(STORAGE_PATH, userId);
        if (!fs.existsSync(userDir)) return res.status(404).json({ error: 'No branding settings found' });

        const settings = {};
        const logoPath = path.join(userDir, 'logo.png');
        if (fs.existsSync(logoPath)) settings.logo = `/branding_assets/${userId}/logo.png`;

        const colorSchemePath = path.join(userDir, 'color_scheme.json');
        if (fs.existsSync(colorSchemePath)) settings.colorScheme = JSON.parse(fs.readFileSync(colorSchemePath, 'utf-8'));

        const fontPreferencesPath = path.join(userDir, 'font_preferences.json');
        if (fs.existsSync(fontPreferencesPath)) settings.fontPreferences = JSON.parse(fs.readFileSync(fontPreferencesPath, 'utf-8'));

        res.json(settings);
    } catch (error) {
        res.status(500).json({ error: 'Failed to retrieve branding settings' });
    }
});

module.exports = router;