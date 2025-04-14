import { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { table_data, table_type } = req.body;
    
    if (!table_data) {
      return res.status(400).json({ error: 'No table data provided' });
    }
    
    // Forward the request to the backend API
    const apiUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
    const response = await axios.post(`${apiUrl}/api/financial/analyze-data`, {
      table_data,
      table_type: table_type || 'unknown'
    });
    
    // Return the response from the backend
    return res.status(200).json(response.data);
  } catch (error) {
    console.error('Error analyzing data:', error);
    return res.status(500).json({ 
      error: 'Error analyzing data', 
      detail: error.response?.data?.detail || error.message 
    });
  }
}
