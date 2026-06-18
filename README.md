# 🚀 Automated Content Syndicator & Archive Backfiller

<div align="center">
  <p><strong>An autonomous pipeline for content syndication and archival drip-feeding to Dev.to.</strong></p>
  <p><em>Engineered by <a href="https://aviperera.com">Avi Perera</a></em></p>
  <p>
    <a href="https://aviperera.com">Website</a> •
    <a href="https://twitter.com/aviperera_">Twitter</a> •
    <a href="https://www.researchgate.net/profile/Avi-Perera">ResearchGate</a> •
    <a href="https://orcid.org/0009-0005-1903-6868">ORCID</a>
  </p>
  <hr>
</div>

## 📌 Overview

This repository houses an autonomous Python engine designed to maximize SEO and Domain Authority through the principle of "Write Once, Publish Everywhere" (WOPE). It watches a primary WordPress installation and programmatically syndicates content to high-authority developer networks.

### Features
*   **Zero-Maintenance Syndication:** Automatically detects new articles published on WordPress and pushes them to Dev.to.
*   **Intelligent Archive Drip-Feeding:** If no new content is published on a given day, the engine paginates backward through the WordPress REST API to find the oldest un-syndicated article and publishes it. This slowly and passively backfills the entire historical archive.
*   **SEO & Canonical Integrity:** All syndicated posts are hardcoded with a `canonical_url` pointing directly back to the original source, ensuring 100% of the SEO juice flows to the primary domain.

## 🛠 Architecture

*   **Language:** Python 3.10
*   **APIs Leveraged:** WordPress REST API, Dev.to REST API
*   **Automation:** GitHub Actions (cron-triggered every 6 hours)
*   **State Management:** Local `posted.json` tracking committed automatically by the Action bot to prevent duplicates.

## 🔗 Related Resources & Authority Insights

To dive deeper into the intersection of technology, law, and international security, explore the following curated resources:

*   **[Avi Perera | Official Website](https://aviperera.com)** - Read the latest articles on Sovereign Algorithms and AI Governance.
*   **[Sovereign Dashboard](https://sovdash.com)** - An interactive analysis platform for state-level AI capabilities.
*   **[The LAWS Framework](https://github.com/a-vip/ai-governance-laws-frameworks)** - Legal analysis frameworks regarding artificial intelligence governance.
*   **[AI Governance Research Aggregator](https://github.com/a-vip/ai-governance-research-aggregator)** - An autonomous index of the latest academic papers.

<br>

<div align="center">
  <small><em>This repository is fully autonomous and powered by GitHub Actions.</em></small><br>
  <small><em>Copyright © Avi Perera.</em></small>
</div>
