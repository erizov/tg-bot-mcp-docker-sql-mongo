# Notes Bot Dashboard Frontend

A modern, responsive web dashboard for monitoring and managing the Notes Bot database backends.

## Features

- **Real-time Dashboard**: Monitor all database backends (SQLite, MongoDB, Neo4j, PostgreSQL, Cassandra, Progress)
- **Advanced Search**: Search across all databases with filters
- **Performance Reports**: Generate and view performance comparisons
- **Live Monitoring**: Real-time system metrics and health monitoring
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern UI**: Clean, intuitive interface with dark mode support

## Technology Stack

- **HTML5**: Semantic markup with accessibility features
- **CSS3**: Modern styling with CSS Grid, Flexbox, and custom properties
- **JavaScript**: ES6+ with modular architecture
- **Chart.js**: Interactive charts and graphs
- **Font Awesome**: Icon library
- **Responsive Design**: Mobile-first approach

## File Structure

```
frontend/
├── index.html              # Main HTML file
├── styles/
│   ├── main.css           # Core styles and layout
│   ├── components.css     # Component-specific styles
│   └── responsive.css     # Responsive design and media queries
├── js/
│   ├── app.js             # Main application logic
│   ├── api.js             # API client and utilities
│   ├── components.js      # UI components and utilities
│   └── charts.js          # Chart management and utilities
└── README.md              # This file
```

## Getting Started

### Prerequisites

- A running Notes Bot backend with FastAPI monitor (port 8001)
- Modern web browser with JavaScript enabled
- Optional: Local web server for development

### Installation

1. **Clone or download** the frontend files to your web server
2. **Ensure the backend** is running on `http://localhost:8001`
3. **Open** `index.html` in your web browser

### Development Setup

For local development, you can use any static file server:

```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx serve .

# Using PHP
php -S localhost:8000
```

Then open `http://localhost:8000` in your browser.

## Usage

### Dashboard Tab

- **Database Status**: View real-time status of all database backends
- **Performance Chart**: Compare insert/lookup times across databases
- **Health Indicators**: Visual status indicators for each database

### Search Tab

- **Database Selection**: Choose which database to search
- **Search Filters**: Filter by title, content, or reminders
- **Results Display**: View search results with actions

### Reports Tab

- **Generate Report**: Create performance analysis reports
- **Export HTML**: Download reports for offline viewing
- **Performance Metrics**: Detailed performance comparisons

### Monitoring Tab

- **Real-time Monitoring**: Live system metrics
- **Health Metrics**: Database health status
- **Activity Log**: Recent system activities
- **Configurable Refresh**: Adjustable update intervals

## API Integration

The frontend communicates with the Notes Bot backend through REST API endpoints:

- `GET /health?db={database}` - Database health check
- `GET /search?q={query}&db={database}` - Search notes
- `GET /report` - Generate performance report
- `GET /metrics` - System metrics
- `GET /stats?db={database}` - Database statistics

## Customization

### Styling

The CSS uses CSS custom properties (variables) for easy theming:

```css
:root {
    --primary-color: #2563eb;
    --secondary-color: #64748b;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --background-color: #f8fafc;
    --surface-color: #ffffff;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
}
```

### Dark Mode

Dark mode is automatically enabled based on system preferences:

```css
@media (prefers-color-scheme: dark) {
    :root {
        --background-color: #0f172a;
        --surface-color: #1e293b;
        --text-primary: #f1f5f9;
        /* ... other dark mode variables */
    }
}
```

### Adding New Charts

Use the ChartManager class to create custom charts:

```javascript
const chart = chartManager.createChart('myChart', {
    type: 'bar',
    data: {
        labels: ['A', 'B', 'C'],
        datasets: [{
            label: 'My Data',
            data: [1, 2, 3],
            backgroundColor: '#3B82F6'
        }]
    }
});
```

## Browser Support

- **Chrome**: 60+
- **Firefox**: 55+
- **Safari**: 12+
- **Edge**: 79+

## Performance

- **Lazy Loading**: Charts and components load on demand
- **Efficient Updates**: Minimal DOM manipulation
- **Responsive Images**: Optimized for different screen sizes
- **Caching**: API responses cached for better performance

## Accessibility

- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: ARIA labels and semantic HTML
- **High Contrast**: Support for high contrast mode
- **Reduced Motion**: Respects user motion preferences

## Troubleshooting

### Common Issues

1. **Charts not loading**: Ensure Chart.js is loaded before the charts script
2. **API errors**: Check that the backend is running on port 8001
3. **Styling issues**: Clear browser cache and reload
4. **Mobile layout**: Ensure viewport meta tag is present

### Debug Mode

Enable debug logging by opening browser console and running:

```javascript
localStorage.setItem('debug', 'true');
```

## Contributing

1. Follow the existing code style
2. Test on multiple browsers
3. Ensure accessibility compliance
4. Update documentation as needed

## License

This frontend is part of the Notes Bot project and follows the same license terms.
