# Marqd: Digital Asset Protection

Marqd is an enterprise-grade digital asset protection platform designed to seamlessly authenticate, discover, and enforce copyright over digital media (images and video) across the web.

Built with a robust **3-Layer Architecture**, Marqd leverages cryptographic watermarking, perceptual hashing, and Google Gemini AI to automate the traditionally manual and expensive process of finding and taking down pirated content.

---

## 🏗 Architecture

Marqd operates across three distinct security layers:

1. **Authentication Layer (Layer 1)**
   - **Invisible Cryptographic Watermarks:** Uses DWT+DCT (Discrete Wavelet Transform + Discrete Cosine Transform) to invisibly embed a unique Asset ID into the media. It is highly robust and survives aggressive compression and resizing.
   - **Perceptual Hashing (pHash):** Acts as a structural fallback. If the watermark is cropped out, the system uses a 16x16 perceptual hash to identify structurally identical media.

2. **Discovery Layer (Layer 2)**
   - **Web Scraping:** Integrates with SerpApi to execute Google Reverse Image searches, finding unauthorized usage across domains.
   - **Video Scanning:** Monitors the YouTube Data API. When suspicious videos are found, it extracts publicly available video metadata and thumbnails for verification purposes.

3. **Intelligence Layer (Layer 3)**
   - **AI Classification:** Utilizes Google Gemini (`gemini-3.1-flash-lite`) to analyze domains and classify them as Authorized, Suspicious, or Violations.
   - **Automated Enforcement:** Dynamically generates professional, PDF-formatted DMCA takedown notices using the forensic evidence gathered (Watermark match + pHash distance).

---

## 🛠 Tech Stack

- **Backend:** Python 3.11, Flask, SQLAlchemy, OpenCV, `blind_watermark`, `imagehash`
- **Frontend:** React 19, Vite, Tailwind CSS (Glassmorphism UI), `react-leaflet`
- **Infrastructure:** Docker, Docker Compose, Nginx (ready for Google Cloud Run deployment)
- **AI/APIs:** Google Gemini Flash, SerpApi, YouTube Data API v3

---

## 🚀 Running Locally

The easiest way to run the entire stack locally is using Docker Compose.

### Prerequisites
- Docker and Docker Compose installed
- API Keys for Google Gemini, SerpApi, and YouTube (Optional for local testing if `USE_MOCK_APIS=true` is set).

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/marqd.git
   cd marqd
   ```

2. **Configure Environment Variables**
   Create a `.env` file in the `backend/` directory:
   ```env
   FLASK_ENV=development
   USE_MOCK_APIS=true
   SECRET_KEY=your-local-secret-key
   DATABASE_URL=sqlite:///marqd.db
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the Application**
   - **Frontend:** `http://localhost:8081`
   - **Backend API:** `http://localhost:8080/api/health`

---

## 🔒 Security & Privacy
- **Zero False Positives:** The dual-layer verification logic ensures DMCA reports are only generated for mathematically proven matches.
- **Data Privacy:** Local execution runs on an isolated SQLite database. Production environments connect securely to Cloud SQL and Google Cloud Storage.
- **Compliance:** AI is utilized purely for classification and document generation; cryptographic hashing remains the absolute source of truth for ownership.