# SoDA Project Backend Setup

## MongoDB Setup

Your Django API requires MongoDB to be running. Here are the options:

### Option 1: Local MongoDB Installation
1. Download and install MongoDB Community Server from https://www.mongodb.com/try/download/community
2. Start MongoDB service:
   - Windows: Run `net start MongoDB` in Command Prompt as Administrator
   - Or start MongoDB manually: `mongod --dbpath C:\data\db`

### Option 2: MongoDB Atlas (Cloud)
1. Create a free account at https://www.mongodb.com/atlas
2. Create a new cluster
3. Get your connection string
4. Create a `.env` file in the project root with:
   ```
   MONGO_URI=your_mongodb_atlas_connection_string
   ```

### Option 3: Docker (if you have Docker installed)
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## Environment Variables
Create a `.env` file in the project root with:
```
MONGO_URI=mongodb://localhost:27017/
```

## Running the API
1. Install dependencies: `pip install -r requirements.txt`
2. Start Django server: `python manage.py runserver`
3. Test API: `python test_api.py`

## API Endpoints
- GET `/api/papers/` - List all papers
- GET `/api/papers/{paper_id}/` - Get specific paper
