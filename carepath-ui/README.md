# CarePath Web Interface

Modern chat interface for CarePath medical triage assistant, built with React, TypeScript, and shadcn/ui.

## Features

- **Chat Interface**: Claude/ChatGPT-style conversation UI
- **Smart Diagnosis Button**: Appears after 3 follow-up questions
- **Auto-Diagnosis**: Triggers automatically at 90%+ confidence
- **Disclaimer Display**: Shows important medical disclaimer with assessment
- **Responsive Design**: Built with Tailwind CSS and shadcn/ui components

## Setup

### 1. Install Dependencies

```bash
cd carepath-ui
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will run at `http://localhost:5173`

## Usage

1. Start the backend server first (see root README)
2. Start the frontend dev server
3. Open browser to `http://localhost:5173`
4. Chat with CarePath about your symptoms
5. After 3 exchanges, click "Ready for Diagnosis" or wait for auto-diagnosis

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **shadcn/ui** components
- **Axios** for API calls
- **Lucide React** for icons
