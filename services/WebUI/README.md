# PDF to Podcast - Web UI

Modern, responsive web interface for creating and managing AI-generated podcasts from PDF documents.

## Features

### 🎨 Style Templates
- 6 pre-configured podcast styles
- Professional Business, Casual Conversation, Educational, Storytelling, News Analysis, Comedy
- Optimized voice settings and LLM parameters for each style

### 📝 Podcast Creation
- Drag & drop PDF upload
- Template selection
- Custom voice settings
- Duration control
- Custom instructions

### 📊 Real-Time Progress
- WebSocket-based live updates
- Progress percentage and ETA
- Token usage and cost tracking
- Step-by-step workflow visualization

### 📥 Multi-Format Export
- SRT subtitles
- VTT web subtitles
- Plain text transcript
- Markdown with metadata
- JSON with timing data

### 🎙️ Podcast Management
- Browse all generated podcasts
- Version history
- Download audio files
- Export transcripts

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **React Query** - Data fetching
- **React Router** - Navigation
- **Axios** - HTTP client
- **Lucide React** - Icons

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Backend API service running on port 8002

### Installation

```bash
# Install dependencies
cd services/WebUI
npm install
```

### Development

```bash
# Start development server
npm run dev

# Navigate to http://localhost:3000
```

The dev server includes:
- Hot module replacement
- Proxy to backend API (localhost:8002)
- WebSocket proxy for real-time updates

### Build for Production

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/        # Reusable UI components
│   ├── ProgressTracker.tsx
│   └── TemplateSelector.tsx
├── pages/            # Page components
│   ├── CreatePodcast.tsx
│   ├── MyPodcasts.tsx
│   ├── EditPodcast.tsx
│   └── Templates.tsx
├── utils/            # Utilities
│   └── api.ts       # API client
├── styles/           # Global styles
│   └── index.css
├── types.ts          # TypeScript types
├── App.tsx           # Main app component
└── main.tsx          # Entry point
```

## API Integration

The UI communicates with the backend API via:

### REST Endpoints
- `GET /api/v1/templates` - List style templates
- `GET /api/v1/templates/{id}` - Get template details
- `POST /process_pdf` - Create podcast
- `GET /status/{job_id}` - Get job status
- `GET /api/v1/podcast/{job_id}/export/{format}` - Export transcript
- `GET /saved_podcasts` - List user's podcasts

### WebSocket
- `ws://localhost:8002/ws/status/{job_id}` - Real-time status updates

## Features in Detail

### Style Templates

Each template includes:
- Voice stability and expressiveness settings
- LLM temperature and top_p configuration
- Custom prompt instructions
- Pacing and tone guidelines

Example templates:
- **Professional Business**: 85% stability, 60% temperature, formal tone
- **Casual Conversation**: 50% stability, 85% temperature, relaxed tone
- **Educational**: 80% stability, 70% temperature, explanatory approach

### Progress Tracking

Real-time progress updates include:
- Current step (PDF Processing, Dialogue Generation, TTS)
- Percentage complete per step
- Overall progress
- Estimated time to completion
- Token usage
- Estimated cost

### Export Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| SRT | .srt | Video subtitles, accessibility |
| VTT | .vtt | HTML5 video subtitles |
| TXT | .txt | Reading, archiving |
| Markdown | .md | Documentation, blogs |
| JSON | .json | Data processing, integration |

## Configuration

### Proxy Configuration

The Vite dev server proxies API requests to the backend:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': 'http://localhost:8002',
    '/ws': {
      target: 'ws://localhost:8002',
      ws: true,
    },
  },
}
```

### Environment Variables

Create `.env` file for custom configuration:

```bash
VITE_API_URL=http://localhost:8002
VITE_WS_URL=ws://localhost:8002
```

## Deployment

### Docker

```bash
# Build
docker build -t pdf-to-podcast-ui .

# Run
docker run -p 3000:80 pdf-to-podcast-ui
```

### Static Hosting

The built files in `dist/` can be served by:
- Nginx
- Apache
- Netlify
- Vercel
- AWS S3 + CloudFront

Example Nginx config:

```nginx
server {
  listen 80;
  server_name example.com;
  root /var/www/pdf-to-podcast-ui;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  location /api {
    proxy_pass http://backend:8002;
  }

  location /ws {
    proxy_pass http://backend:8002;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }
}
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Performance

- Code splitting by route
- Lazy loading of components
- Optimized build with Vite
- Tree shaking
- Asset optimization

## Future Enhancements

- [ ] Real-time collaborative editing
- [ ] Segment-level regeneration UI
- [ ] Audio waveform visualization
- [ ] Inline transcript editing
- [ ] Drag & drop segment reordering
- [ ] Voice sample upload
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Mobile app (React Native)

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

Same as parent project (see root LICENSE file)

## Support

For issues or questions:
- Check API documentation
- Review browser console for errors
- Verify backend API is running
- File GitHub issue with details
