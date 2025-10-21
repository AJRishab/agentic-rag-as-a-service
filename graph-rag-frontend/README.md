# Graph RAG Frontend

A modern React frontend for the Graph RAG Platform, providing an intuitive interface for document upload, knowledge graph visualization, and agentic querying.

## Features

- **Document Upload**: Drag-and-drop interface for PDF, DOCX, and TXT files
- **Real-time Processing**: Live pipeline visualization with agent activity
- **Knowledge Graph Visualization**: Interactive graph statistics and entity types
- **Agentic Query Interface**: Natural language querying with reasoning chain display
- **Responsive Design**: Modern UI with dark theme and glass morphism effects
- **Real-time Status**: Backend connection monitoring and error handling

## Quick Start

### Prerequisites

- Node.js 16+ and npm
- Graph RAG Backend running on port 8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The application will open at http://localhost:3000

### Production Build

```bash
# Build for production
npm run build

# Serve production build
npm run serve
```

## Project Structure

```
graph-rag-frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── App.js              # Main application component
│   ├── index.js            # React entry point
│   ├── index.css           # Global styles with Tailwind
│   └── components/         # Reusable components (future)
├── package.json
├── tailwind.config.js      # Tailwind CSS configuration
└── README.md
```

## Configuration

### Backend URL

The frontend connects to the backend at `http://localhost:8000` by default. To change this:

1. Edit `src/App.js`
2. Update the `API_BASE_URL` constant
3. Or set up a proxy in `package.json`

### Styling

The application uses Tailwind CSS with custom color schemes and animations. Key features:

- Dark theme with purple/pink gradients
- Glass morphism effects
- Responsive grid layouts
- Custom animations and transitions

## API Integration

The frontend integrates with the Graph RAG Backend API:

- **Health Check**: `GET /health`
- **Document Upload**: `POST /api/documents/upload`
- **Document List**: `GET /api/documents`
- **Graph Stats**: `GET /api/graph/stats`
- **Query**: `POST /api/query`

## Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run serve` - Serve production build

### Adding Components

1. Create new components in `src/components/`
2. Import and use in `App.js`
3. Follow the existing styling patterns

## Deployment

### Docker

```bash
# Build Docker image
docker build -t graph-rag-frontend .

# Run container
docker run -p 3000:3000 graph-rag-frontend
```

### Static Hosting

The built application can be deployed to any static hosting service:

- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages

## Troubleshooting

### Backend Connection Issues

1. Ensure the Graph RAG Backend is running on port 8000
2. Check CORS settings in the backend
3. Verify the API_BASE_URL in the frontend

### Build Issues

1. Clear node_modules and reinstall: `rm -rf node_modules && npm install`
2. Clear npm cache: `npm cache clean --force`
3. Check Node.js version compatibility

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details
