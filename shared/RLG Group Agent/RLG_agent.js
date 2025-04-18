// RLG_agent.js - AI-Powered Marketing & Content Automation for RLG Data & RLG Fans

const axios = require("axios");
const fs = require("fs");
const schedule = require("node-schedule");
const nodemailer = require("nodemailer");
require("dotenv").config();

// Configuration
const CONFIG = {
    openai_api_key: process.env.OPENAI_API_KEY,
    deepseek_api_key: process.env.DEEPSEEK_API_KEY,
    mailing_list_file: "./mailing_list.json",
    email_sender: process.env.EMAIL_SENDER,
    email_password: process.env.EMAIL_PASSWORD,
    posting_schedule: ["08:00", "12:00", "16:00", "20:00"], // Posts four times a day
};

// AI Content Generator (ChatGPT & DeepSeek)
async function generateMarketingContent(prompt) {
    try {
        const response = await axios.post(
            "https://api.deepseek.com/v1/chat/completions",
            {
                model: "deepseek-llm-1.3b",
                messages: [{ role: "user", content: prompt }],
                max_tokens: 500,
                temperature: 0.8,
            },
            {
                headers: { Authorization: `Bearer ${CONFIG.deepseek_api_key}` },
            }
        );

        return response.data.choices[0].message.content;
    } catch (error) {
        console.error("Error generating content:", error);
        return "Error: Unable to generate marketing content.";
    }
}

// AI Image & Video Generator (OpenAI Sora)
async function generateMedia(prompt, type = "image") {
    try {
        const endpoint =
            type === "video"
                ? "https://api.openai.com/v1/videos"
                : "https://api.openai.com/v1/images";
        
        const response = await axios.post(
            endpoint,
            { prompt },
            {
                headers: {
                    Authorization: `Bearer ${CONFIG.openai_api_key}`,
                    "Content-Type": "application/json",
                },
            }
        );

        return response.data.url;
    } catch (error) {
        console.error(`Error generating ${type}:`, error);
        return `Error: Unable to generate ${type}.`;
    }
}

// Post Content Across Platforms
async function postToSocialMedia(content, mediaUrl) {
    console.log("Posting to social media:", content, mediaUrl);
    // TODO: Integrate API calls for Twitter, LinkedIn, Facebook, and Instagram.
}

// Automated Email Marketing
async function sendMarketingEmail(subject, body) {
    const mailingList = JSON.parse(fs.readFileSync(CONFIG.mailing_list_file, "utf8"));

    let transporter = nodemailer.createTransport({
        service: "Gmail",
        auth: {
            user: CONFIG.email_sender,
            pass: CONFIG.email_password,
        },
    });

    for (let recipient of mailingList) {
        let mailOptions = {
            from: CONFIG.email_sender,
            to: recipient.email,
            subject: subject,
            text: body,
        };

        await transporter.sendMail(mailOptions);
        console.log(`Email sent to ${recipient.email}`);
    }
}

// Daily Scheduled Posting
CONFIG.posting_schedule.forEach((time) => {
    schedule.scheduleJob(time, async function () {
        const marketingText = await generateMarketingContent(
            "Create an engaging post promoting RLG Data & RLG Fans with current trends."
        );
        const imageUrl = await generateMedia("Create an ad image for RLG Data & RLG Fans.");
        await postToSocialMedia(marketingText, imageUrl);
    });
});

// Weekly Newsletter
schedule.scheduleJob("0 9 * * 1", async function () {
    const newsletterContent = await generateMarketingContent(
        "Write a professional and engaging weekly newsletter for RLG Data & RLG Fans."
    );
    await sendMarketingEmail("Weekly Insights from RLG Data & RLG Fans", newsletterContent);
});

console.log("RLG Agent is running...");
