import { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { image_base64, lang } = req.body;
    
    if (!image_base64) {
      return res.status(400).json({ error: 'No image provided' });
    }
    
    // Forward the request to the backend API
    const apiUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
    const response = await axios.post(`${apiUrl}/api/financial/detect-tables`, {
      image_base64,
      lang: lang || 'heb+eng'
    });
    
    // Return the response from the backend
    return res.status(200).json(response.data);
  } catch (error) {
    console.error('Error detecting tables:', error);
    return res.status(500).json({ 
      error: 'Error detecting tables', 
      detail: error.response?.data?.detail || error.message 
    });
  }
}
