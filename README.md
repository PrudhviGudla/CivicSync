# CivicSync

[![Python](https://img.shields.io/badge/python-v3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0-green.svg)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://www.mongodb.com/cloud/atlas)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)

CivicSync is a modern, fullstack civic issue reporting and analytics platform developed through "vibe coding" - an exploratory, iterative development approach. It empowers citizens to report, track, and vote on local issues, and provides real-time analytics and map-based visualizations for community engagement and transparency.

> **Note**: This project was developed by "vibe coding", where the architecture and features evolved organically based on user needs

## Live Demo
🌐 **Demo URL:** [civicsync-jdk1.onrender.com](https://civicsync-jdk1.onrender.com/)

> **Note:** The application is hosted on Render's free tier. Initial access may experience a 30-60 second cold start delay after periods of inactivity. Subsequent requests will be faster.

## Features
- **User Authentication**: Register/login securely with email and password (JWT-based).
- **Report Issues**: Submit civic issues with title, description, category, location, and optional image upload.
- **My Issues Dashboard**: View, edit, delete, and update the status of your own issues.
- **Public Issue Feed**: Paginated, searchable, filterable, and sortable list of all public issues.
- **Voting System**: Vote once per issue to surface priority for resolution.
- **Analytics Dashboard**: Visualize issue trends, category breakdowns, and most-voted issues with interactive charts.
- **Map View**: See all issues on a map, with clustering and sidebar details. <!-- - **Chatbot Assistant**: AI-powered assistant (Groq + LangChain) to answer questions, search issues, provide analytics, and accept feedback. -->
- **Modern, Responsive UI**: Beautiful, animated, and mobile-friendly design.

## Tech Stack
- **Backend**: FastAPI (Python), MongoDB (Atlas), Cloudinary (image storage)
- **Frontend**: HTML, CSS, JavaScript (vanilla, no framework)<!-- - **AI Chatbot**: LangChain + GroqAPI (LLM) -->
- **Deployment**: Render.com
- **Containerization**: Docker and Docker Compose

**Note:** This application is tested with Python 3.13. Other versions may work but are not tested

## Setup Instructions

You can set up CivicSync either using traditional Python installation or using Docker. Choose the method that best suits your needs.

### Prerequisites
- Python 3.13+ (if running locally)
- Docker and Docker Compose (if using containerized setup)
- Git

### 1. Clone the Repository
```sh
git clone https://github.com/yourusername/civicsync.git
cd civicsync
```

### 2. Create and Activate a Virtual Environment (If running locally)
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies (If running locally)
```sh
pip install -r requirements.txt
```

### 4. Setting Up MongoDB Atlas (Free Tier)
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Once your account is created, you'll be automatically directed to your first cluster
3. From your cluster view:
   - Click the "Connect" button
   - Choose "Drivers" under "Connect to your application"
   - Copy the connection string that looks like: `mongodb+srv://<username>:<password>@your-cluster.mongodb.net/?retryWrites=true&w=majority`
   - Replace `<username>` and `<password>` with the values shown in the Atlas interface

Important Note About IP Access:
- By default, MongoDB Atlas requires IP whitelisting
- For development and deployment, you have two options:
  1. Allow access from anywhere (easiest but less secure):
     - Go to Network Access → Add IP Address → Allow Access from Anywhere
     - This adds `0.0.0.0/0` to the whitelist
  2. Restrict to specific IPs (more secure):
     - Add your local development machine's IP
     - Add your Render deployment URL's IP
     - You can find your current IP at [whatismyip.com](https://whatismyip.com)
     - For Render, you'll need to add the IP after deployment

### 5. Configure Environment Variables
Create a `.env` file in the root directory:
```
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
SECRET_KEY=your_secret_key_here # Secret for JWT signing
CLOUDINARY_UPLOAD_URL=your_cloudinary_upload_url_here
CLOUDINARY_UPLOAD_PRESET=your_cloudinary_upload_preset_here
```

### 6. Setting up Cloudinary
1. Sign up for a free account at [Cloudinary](https://cloudinary.com/)
2. From your Cloudinary dashboard:
   - Go to Settings > Upload
   - Scroll down to "Upload presets"
   - Click "Add upload preset"
   - Set "Upload preset name" (remember this for CLOUDINARY_UPLOAD_PRESET)
   - Change "Signing Mode" to "Unsigned"
   - Save the preset
3. Get your upload URL:
   - Format: `https://api.cloudinary.com/v1_1/YOUR_CLOUD_NAME/image/upload`
   - Replace YOUR_CLOUD_NAME with your Cloudinary cloud name
   - Set this as CLOUDINARY_UPLOAD_URL in .env
4. Additional settings:
   - In your Cloudinary settings, ensure CORS is configured
   - Add your deployment URL to allowed origins
   - Set "Resource type" to "Auto" in upload preset

### 7. Running the Application

#### Option 1: Run Locally with Python
```sh
uvicorn main:app --reload
```
Visit [http://localhost:8000](http://localhost:8000)

#### Option 2: Run with Docker
If you have Docker installed, you can run the application in a container:

```sh
# Build and start the container
docker-compose up --build

# To run in detached mode
docker-compose up -d
```
Visit [http://localhost:8000](http://localhost:8000)

The Docker setup:
- Uses Python 3.13
- Automatically loads environment variables from `.env`
- Includes hot-reload for development
- Runs with multiple workers for better performance

To stop the Docker container:
```sh
docker-compose down
```

### 8. Deploying (Render.com)
- Push your code to GitHub.
- Create a new Web Service on [Render.com](https://render.com/).
- Set the build command: `pip install -r requirements.txt`
- Set the start command: `uvicorn main:app --host 0.0.0.0 --port 10000`
- Add all environment variables in the Render dashboard.
- Deploy and get your public URL!

## How It Works
- **Authentication**: JWT tokens in cookies, checked on every protected route.
- **Issue Reporting**: Users submit issues with optional images (uploaded to Cloudinary).
- **Voting**: Each user can vote once per issue; votes are tracked in MongoDB.
- **Analytics**: Charts are generated from MongoDB aggregations.
- **Map**: Issues are geocoded and shown as markers with clustering and sidebar details.
<!-- - **Chatbot**: The floating chat button opens an AI assistant that can answer questions, search issues, provide analytics, and accept feedback (which is saved as an issue in the DB). -->

## Chatbot Features to be Added:
- Click the Chat button in the top right to open the chatbot.
- Ask about CivicSync features, how to use the app, or request analytics (e.g., "Show me pending issues", "How many issues are resolved?").
- You can also report bugs or feedback directly to the chatbot.

## Understanding JWT Authentication
JSON Web Tokens (JWT) are used in CivicSync for secure, stateless authentication. When users log in (`/login` route), the server:
1. Validates their credentials
2. Generates a JWT containing the user's ID
3. Signs it with a secret key
4. Sends it as an HTTP-only cookie

This token is automatically included in subsequent requests, allowing the server to verify the user's identity without database queries. The `require_user` function in `main.py` validates these tokens for protected routes like issue reporting and voting.


