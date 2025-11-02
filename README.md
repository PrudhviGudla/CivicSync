# CivicSync

CivicSync is a modern, fullstack civic issue reporting and analytics platform. It empowers citizens to report, track, and vote on local issues, and provides real-time analytics and map-based visualizations for community engagement and transparency.

## Features
- **User Authentication**: Register/login securely with email and password (JWT-based).
- **Report Issues**: Submit civic issues with title, description, category, location, and optional image upload.
- **My Issues Dashboard**: View, edit, delete, and update the status of your own issues.
- **Public Issue Feed**: Paginated, searchable, filterable, and sortable list of all public issues.
- **Voting System**: Vote once per issue to surface priority for resolution.
- **Analytics Dashboard**: Visualize issue trends, category breakdowns, and most-voted issues with interactive charts.
- **Map View**: See all issues on a map, with clustering and sidebar details.
- **Chatbot Assistant**: AI-powered assistant (Groq + LangChain) to answer questions, search issues, provide analytics, and accept feedback.
- **Modern, Responsive UI**: Beautiful, animated, and mobile-friendly design.

## Tech Stack
- **Backend**: FastAPI (Python), MongoDB (Atlas), Cloudinary (image storage)
- **Frontend**: HTML, CSS, JavaScript (vanilla, no framework)
- **AI Chatbot**: LangChain + GroqAPI (LLM)
- **Deployment**: Render.com (or Railway)

## Setup Instructions

### 1. Clone the Repository
```sh
git clone https://github.com/yourusername/civicsync.git
cd civicsync
```

### 2. Create and Activate a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```
MONGO_URI=your_mongodb_uri_here
SECRET_KEY=your_secret_key_here # Secret for JWT signing
CLOUDINARY_UPLOAD_URL=your_cloudinary_upload_url_here
CLOUDINARY_UPLOAD_PRESET=your_cloudinary_upload_preset_here
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the App Locally
```sh
uvicorn main:app --reload
```
Visit [http://localhost:8000](http://localhost:8000)

### 6. Deploying (Render.com)
- Push your code to GitHub.
- Create a new Web Service on [Render.com](https://render.com/).
- Set the build command: `pip install -r requirements.txt`
- Set the start command: `uvicorn main:app --host 0.0.0.0 --port 10000`
- Add all environment variables in the Render dashboard.
- Deploy and get your public URL!

## Environment Variables
- `MONGO_URI`: MongoDB Atlas connection string
- `SECRET_KEY`: Secret for JWT signing
- `CLOUDINARY_UPLOAD_URL`: Cloudinary API endpoint
- `CLOUDINARY_UPLOAD_PRESET`: Cloudinary unsigned upload preset
<!-- - `GROQ_API_KEY`: API key for Groq LLM -->

## How It Works
- **Authentication**: JWT tokens in cookies, checked on every protected route.
- **Issue Reporting**: Users submit issues with optional images (uploaded to Cloudinary).
- **Voting**: Each user can vote once per issue; votes are tracked in MongoDB.
- **Analytics**: Charts are generated from MongoDB aggregations.
- **Map**: Issues are geocoded and shown as markers with clustering and sidebar details.
- **Chatbot**: The floating chat button opens an AI assistant that can answer questions, search issues, provide analytics, and accept feedback (which is saved as an issue in the DB).

## Chatbot Usage (Feature to be Added)
- Click the Chat button in the top right to open the chatbot.
- Ask about CivicSync features, how to use the app, or request analytics (e.g., "Show me pending issues", "How many issues are resolved?").
- You can also report bugs or feedback directly to the chatbot.

