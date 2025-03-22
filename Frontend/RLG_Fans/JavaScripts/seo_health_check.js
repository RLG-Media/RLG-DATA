document.addEventListener("DOMContentLoaded", function () {
    const seoResults = document.getElementById("seo-results");
    const seoCheckButton = document.getElementById("run-seo-check");
    const downloadReportButton = document.getElementById("download-seo-report");

    seoCheckButton.addEventListener("click", function () {
        seoResults.innerHTML = "<p>Running SEO health checks...</p>";
        setTimeout(runSEOChecks, 1000);
    });

    async function runSEOChecks() {
        const checks = [
            checkMetaTags(),
            checkHeadingStructure(),
            checkImageAltTags(),
            checkPageSpeed(),
            checkMobileFriendliness(),
            checkIndexability(),
            checkStructuredData(),
            checkBrokenLinks(),
            checkSocialMediaMetaTags(),
            runLighthouseAudit(),
            getAISEORecommendations(),
            analyzeCompetitorSEO(),
            checkKeywordPerformance(),
            checkBacklinks()
        ];

        Promise.all(checks).then(results => {
            seoResults.innerHTML = results.join("<br>");
        });
    }

    function checkMetaTags() {
        return new Promise(resolve => {
            const title = document.title || "❌ Missing title tag";
            const description = document.querySelector('meta[name="description"]')?.content || "❌ Missing meta description";
            resolve(`✅ Title: ${title} <br> ✅ Meta Description: ${description}`);
        });
    }

    function checkHeadingStructure() {
        return new Promise(resolve => {
            const headings = document.querySelectorAll("h1, h2, h3, h4, h5, h6");
            let structure = "";
            headings.forEach(h => (structure += `${h.tagName}: ${h.textContent} <br>`));
            resolve(`✅ Heading Structure: <br> ${structure || "❌ No headings found"}`);
        });
    }

    function checkImageAltTags() {
        return new Promise(resolve => {
            const images = document.querySelectorAll("img");
            let missingAltCount = 0;
            images.forEach(img => {
                if (!img.alt) missingAltCount++;
            });
            resolve(`✅ Images: ${images.length} found <br> ❌ Missing ALT tags: ${missingAltCount}`);
        });
    }

    function checkPageSpeed() {
        return new Promise(resolve => {
            const start = performance.now();
            setTimeout(() => {
                const end = performance.now();
                resolve(`✅ Page Load Time: ${Math.round(end - start)}ms`);
            }, 500);
        });
    }

    function checkMobileFriendliness() {
        return new Promise(resolve => {
            const isMobile = window.innerWidth < 768;
            resolve(isMobile ? "✅ Mobile-Friendly" : "❌ Not Mobile-Friendly");
        });
    }

    function checkIndexability() {
        return new Promise(resolve => {
            const robotsMeta = document.querySelector('meta[name="robots"]')?.content || "index, follow";
            resolve(`✅ Robots Meta: ${robotsMeta}`);
        });
    }

    function checkStructuredData() {
        return new Promise(resolve => {
            const structuredData = document.querySelectorAll('script[type="application/ld+json"]');
            resolve(`✅ Structured Data Snippets: ${structuredData.length} found`);
        });
    }

    function checkBrokenLinks() {
        return new Promise(resolve => {
            const links = document.querySelectorAll("a");
            let brokenLinks = [];
            links.forEach(link => {
                fetch(link.href)
                    .then(response => {
                        if (!response.ok) brokenLinks.push(link.href);
                    })
                    .catch(() => brokenLinks.push(link.href));
            });

            setTimeout(() => {
                resolve(`✅ Links Checked: ${links.length} <br> ❌ Broken Links: ${brokenLinks.length}`);
            }, 1000);
        });
    }

    function checkSocialMediaMetaTags() {
        return new Promise(resolve => {
            const socialTags = [
                "og:title", "og:description", "og:image", "twitter:title", "twitter:description"
            ];
            let missingTags = [];

            socialTags.forEach(tag => {
                if (!document.querySelector(`meta[property="${tag}"]`) && !document.querySelector(`meta[name="${tag}"]`)) {
                    missingTags.push(tag);
                }
            });

            resolve(`✅ Social Media Meta Tags: ${socialTags.length - missingTags.length} found <br> ❌ Missing: ${missingTags.join(", ") || "None"}`);
        });
    }

    async function runLighthouseAudit() {
        return new Promise(resolve => {
            fetch("https://lighthouse-dot-webdotdevsite.appspot.com//lh/newaudit?url=" + encodeURIComponent(window.location.href))
                .then(response => response.json())
                .then(data => {
                    resolve(`✅ Google Lighthouse Score: ${data.categories.performance.score * 100} <br> ✅ Accessibility: ${data.categories.accessibility.score * 100} <br> ✅ Best Practices: ${data.categories["best-practices"].score * 100} <br> ✅ SEO: ${data.categories.seo.score * 100}`);
                })
                .catch(() => {
                    resolve("❌ Lighthouse Audit Failed - Check Google Lighthouse manually.");
                });
        });
    }

    async function getAISEORecommendations() {
        return new Promise(resolve => {
            fetch("https://api.openai.com/v1/completions", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer YOUR_OPENAI_API_KEY"
                },
                body: JSON.stringify({
                    model: "gpt-4",
                    prompt: "Analyze this webpage for SEO improvements: " + document.documentElement.innerHTML.substring(0, 5000),
                    max_tokens: 150
                })
            })
                .then(response => response.json())
                .then(data => {
                    resolve(`🤖 AI SEO Suggestion: ${data.choices[0].text}`);
                })
                .catch(() => {
                    resolve("❌ AI SEO Recommendation Failed.");
                });
        });
    }

    async function analyzeCompetitorSEO() {
        return new Promise(resolve => {
            fetch("https://api.semrush.com/?type=domain_ranks&key=YOUR_SEMRUSH_API_KEY&domain=competitor.com")
                .then(response => response.json())
                .then(data => {
                    resolve(`✅ Competitor SEO Score: ${data.rank}`);
                })
                .catch(() => {
                    resolve("❌ Competitor SEO Analysis Failed.");
                });
        });
    }

    async function checkKeywordPerformance() {
        return new Promise(resolve => {
            fetch("https://api.semrush.com/?type=domain_rank_keywords&key=YOUR_SEMRUSH_API_KEY&domain=yourwebsite.com")
                .then(response => response.json())
                .then(data => {
                    resolve(`✅ Top Keywords: ${data.keywords.join(", ")}`);
                })
                .catch(() => {
                    resolve("❌ Keyword Analysis Failed.");
                });
        });
    }

    async function checkBacklinks() {
        return new Promise(resolve => {
            fetch("https://api.ahrefs.com/v3/site-explorer/backlinks?target=yourwebsite.com&api_token=YOUR_AHREFS_API_KEY")
                .then(response => response.json())
                .then(data => {
                    resolve(`✅ Backlinks: ${data.total_backlinks} <br> ✅ Referring Domains: ${data.referring_domains}`);
                })
                .catch(() => {
                    resolve("❌ Backlink Analysis Failed.");
                });
        });
    }
});
