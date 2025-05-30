
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Set favicon dynamically
const favicon = document.createElement('link');
favicon.rel = 'icon';
favicon.href = '/logo.png';
document.head.appendChild(favicon);

// Set page title
document.title = 'TunnelGrid.ai - Map the Hidden Network of AI Search';

createRoot(document.getElementById("root")!).render(<App />);
