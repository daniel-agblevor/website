/**
 * API Configuration Module
 * Dynamically switches between local API server and deployed Render backend.
 */
const CONFIG = {
  // Set your Render backend URL here for production GitHub Pages deployment
  PRODUCTION_API_URL: 'https://hr-systems-consulting-api.onrender.com',

  get API_BASE_URL() {
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://127.0.0.1:5000/api';
    }
    // If running on GitHub Pages or custom domain, use production API endpoint
    return `${this.PRODUCTION_API_URL}/api`;
  }
};
