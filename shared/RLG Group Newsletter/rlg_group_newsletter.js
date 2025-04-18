// RLG Group Automated Newsletter System
// Manages content creation, email campaigns, and trend-driven marketing automation.

import axios from "axios";
import OpenAI from "openai";
import nodemailer from "nodemailer";
import cron from "node-cron";
import cheerio from "cheerio";
import fs from "fs";

// ===== Configuration =====
const config = {
    openaiKey: process.env.OPENAI_API_KEY,
    deepseekKey: process.env.DEEPSEEK_API_KEY,
    emailSender: process.env.EMAIL_SENDER,
    emailPassword: process.env.EMAIL_PASSWORD,
    recipientsFile: "./subscribers.json",
    postFrequency: 4, // Number of posts per day
    newsletterSchedule: "0 10 * * *", // Send daily at 10 AM
    scrapeURLs: ["https://rlgdata.com", "https://rlgfans.com"]
};

// Initialize OpenAI Client
const openai = new OpenAI({
    apiKey: config.openaiKey
});

// Initialize Email Transporter
const transporter = nodemailer.createTransport({
    service: "gmail",
    auth: {
        user: config.emailSender,
        pass: config.emailPassword
    }
});

// ===== AI-Generated Content =====
async function generateNewsletterContent() {
    const prompt = `
    Generate a professional, engaging newsletter for RLG Data and RLG Fans.
    Include:
    - Industry trends in data intelligence and content monetization.
    - New RLG features & case studies.
    - Creator success stories.
    - A compelling call-to-action.
    `;
    
    try {
        const response = await openai.chat.completions.create({
            model: "gpt-4",
            messages: [{ role: "system", content: prompt }],
            max_tokens: 800
        });

        return response.choices[0].message.content;
    } catch (error) {
        console.error("Error generating newsletter content:", error);
        return "We encountered an issue generating this week's newsletter.";
    }
}

// ===== AI-Generated Images/Videos (OpenAI Sora) =====
async function generateMarketingMedia() {
    const prompt = "Create a high-quality ad image for RLG Data and RLG Fans featuring content analytics and creator monetization.";
    
    try {
        const response = await axios.post("https://api.openai.com/v1/images/generations", {
            model: "dall-e-3",
            prompt: prompt,
            n: 1,
            size: "1024x1024"
        }, {
            headers: { Authorization: `Bearer ${config.openaiKey}` }
        });

        return response.data.data[0].url;
    } catch (error) {
        console.error("Error generating marketing image:", error);
        return null;
    }
}

// ===== Email Sending =====
async function sendNewsletter() {
    const content = await generateNewsletterContent();
    const imageUrl = await generateMarketingMedia();
    const subscribers = JSON.parse(fs.readFileSync(config.recipientsFile, "utf8"));

    const emailOptions = {
        from: `"Khoto Zulu" <${config.emailSender}>`,
        subject: "🚀 RLG Data & RLG Fans - This Week’s Insights & Monetization Strategies",
        html: `
            <h2>📊 RLG Weekly Insights</h2>
            <p>${content}</p>
            <img src="${imageUrl}" alt="Marketing Image" style="max-width: 100%;">
            <p><a href="https://rlgdata.com/signup" style="padding: 10px; background: #007bff; color: white; text-decoration: none;">Join Now</a></p>
        `
    };

    for (const subscriber of subscribers) {
        emailOptions.to = subscriber.email;
        try {
            await transporter.sendMail(emailOptions);
            console.log(`Newsletter sent to: ${subscriber.email}`);
        } catch (error) {
            console.error(`Error sending to ${subscriber.email}:`, error);
        }
    }
}

// ===== Web Scraping for New Subscribers =====
async function scrapeEmails() {
    let newEmails = [];
    
    for (const url of config.scrapeURLs) {
        try {
            const { data } = await axios.get(url);
            const $ = cheerio.load(data);
            $("a[href^='mailto:']").each((_, el) => {
                const email = $(el).attr("href").replace("mailto:", "");
                if (email && !newEmails.includes(email)) {
                    newEmails.push(email);
                }
            });
        } catch (error) {
            console.error("Error scraping emails from:", url, error);
        }
    }

    if (newEmails.length > 0) {
        let existingEmails = JSON.parse(fs.readFileSync(config.recipientsFile, "utf8"));
        let updatedEmails = [...new Set([...existingEmails, ...newEmails])];
        fs.writeFileSync(config.recipientsFile, JSON.stringify(updatedEmails, null, 2));
        console.log("Updated subscriber list with new emails.");
    }
}

// ===== Social Media Auto-Posting =====
async function generateAndPostSocialMedia() {
    const topics = ["creator monetization", "AI-driven analytics", "trending insights", "content engagement"];
    const topic = topics[Math.floor(Math.random() * topics.length)];

    const prompt = `Create an engaging social media post about ${topic}, promoting RLG Data and RLG Fans.`;

    try {
        const response = await openai.chat.completions.create({
            model: "gpt-4",
            messages: [{ role: "system", content: prompt }],
            max_tokens: 200
        });

        const postContent = response.choices[0].message.content;
        console.log(`Generated Social Media Post: ${postContent}`);

        // Simulating post (replace with API calls to Twitter, LinkedIn, etc.)
        console.log("Auto-posting to social platforms...");
    } catch (error) {
        console.error("Error generating social media content:", error);
    }
}

// ===== Scheduling & Automation =====
cron.schedule(config.newsletterSchedule, async () => {
    console.log("Sending weekly newsletter...");
    await sendNewsletter();
});

cron.schedule("0 */6 * * *", async () => {
    console.log("Auto-posting marketing content...");
    await generateAndPostSocialMedia();
});

cron.schedule("0 0 * * 0", async () => {
    console.log("Scraping new email subscribers...");
    await scrapeEmails();
});

// ===== Execution =====
(async () => {
    console.log("🚀 RLG Marketing Agent Running...");
    await scrapeEmails();
    await generateAndPostSocialMedia();
})();
