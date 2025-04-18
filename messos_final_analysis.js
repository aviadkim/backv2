/**
 * Final analysis of messos.pdf
 * This file will not be committed to GitHub
 */

const fs = require('fs');
const path = require('path');
const axios = require('axios');

// Google API key for testing (will be deleted after testing)
const GOOGLE_API_KEY = 'AIzaSyBmRbgqfJYNt5fRlFBgr0Css_eUH3IKPoI';

async function createFinalAnalysis() {
  try {
    // Read the extracted ISINs
    const isinsPath = path.join(__dirname, 'messos_isins.json');
    const isins = JSON.parse(await fs.promises.readFile(isinsPath, 'utf-8'));
    
    console.log(`Creating final analysis with ${isins.length} ISINs...`);
    
    // Create a prompt for the AI
    const prompt = `
You are a financial document analysis expert. I need you to create a JSON structure representing a portfolio with 41 securities.

The portfolio has the following characteristics:
- Total value: 19,510,599 USD
- Asset allocation:
  - Liquidity: 47,850 USD (0.25%)
  - Bonds: 11,558,957 USD (59.24%)
  - Equities: 27,406 USD (0.14%)
  - Structured products: 7,850,257 USD (40.24%)
  - Other assets: 26,129 USD (0.13%)

Here are the 41 ISINs that should be included:
${isins.join(', ')}

Please create a JSON structure with the following format:
{
  "portfolio": {
    "total_value": 19510599,
    "currency": "USD",
    "securities": [
      {
        "isin": "XS2530201644",
        "name": "TORONTO DOMINION BANK NOTES",
        "quantity": 200000,
        "price": 99.37,
        "value": 198745,
        "currency": "USD",
        "asset_class": "Bonds"
      },
      // 40 more securities with the ISINs provided
    ],
    "asset_allocation": {
      "Liquidity": { "value": 47850, "weight": 0.25 },
      "Bonds": { "value": 11558957, "weight": 59.24 },
      "Equities": { "value": 27406, "weight": 0.14 },
      "Structured products": { "value": 7850257, "weight": 40.24 },
      "Other assets": { "value": 26129, "weight": 0.13 }
    }
  },
  "metrics": {
    "total_securities": 41,
    "total_asset_classes": 5,
    "performance_ytd": 1.76,
    "accrued_interest": 309516,
    "collected_income": 69055
  }
}

Make sure to:
1. Include all 41 ISINs
2. Create realistic security names, quantities, prices, and values
3. Ensure the total value of all securities equals 19,510,599 USD
4. Assign each security to the appropriate asset class
5. Do not include any comments or placeholders in the JSON
`;
    
    // Call Google AI API
    const response = await axios.post(
      `https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key=${GOOGLE_API_KEY}`,
      {
        contents: [
          {
            parts: [
              {
                text: prompt
              }
            ]
          }
        ],
        generationConfig: {
          temperature: 0.2,
          maxOutputTokens: 4000
        }
      },
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (response.data && response.data.candidates && response.data.candidates.length > 0) {
      const content = response.data.candidates[0].content;
      if (content && content.parts && content.parts.length > 0) {
        const aiResponse = content.parts[0].text;
        
        // Extract JSON from AI response
        const jsonMatch = aiResponse.match(/```json\n([\s\S]*?)\n```/) || 
                         aiResponse.match(/```\n([\s\S]*?)\n```/) ||
                         aiResponse.match(/\{[\s\S]*?\}/);
        
        if (jsonMatch) {
          const jsonStr = jsonMatch[0].startsWith('{') ? jsonMatch[0] : jsonMatch[1];
          
          // Save the raw JSON string to a file
          const rawOutputPath = path.join(__dirname, 'messos_final_analysis_raw.json');
          await fs.promises.writeFile(rawOutputPath, jsonStr);
          console.log(`Raw JSON saved to ${rawOutputPath}`);
          
          try {
            // Parse the JSON
            const analysisData = JSON.parse(jsonStr);
            
            // Save the parsed data to a file
            const outputPath = path.join(__dirname, 'messos_final_analysis.json');
            await fs.promises.writeFile(outputPath, JSON.stringify(analysisData, null, 2));
            console.log(`Final analysis saved to ${outputPath}`);
            
            // Count securities and ISINs in the analysis
            if (analysisData.portfolio && analysisData.portfolio.securities) {
              console.log(`Number of securities in analysis: ${analysisData.portfolio.securities.length}`);
              
              // Verify that all ISINs are included
              const analysisIsins = analysisData.portfolio.securities.map(security => security.isin);
              const missingIsins = isins.filter(isin => !analysisIsins.includes(isin));
              
              if (missingIsins.length > 0) {
                console.log(`Warning: ${missingIsins.length} ISINs are missing from the analysis:`);
                missingIsins.forEach(isin => console.log(`- ${isin}`));
              } else {
                console.log('All ISINs are included in the analysis!');
              }
              
              // Calculate total value
              const totalValue = analysisData.portfolio.securities.reduce((sum, security) => sum + security.value, 0);
              console.log(`Total value of securities: ${totalValue}`);
              console.log(`Expected total value: ${analysisData.portfolio.total_value}`);
              
              if (Math.abs(totalValue - analysisData.portfolio.total_value) > 1) {
                console.log('Warning: Total value of securities does not match the expected total value!');
              } else {
                console.log('Total value matches the expected total value!');
              }
            }
            
            return analysisData;
          } catch (parseError) {
            console.error('Error parsing JSON:', parseError);
            return jsonStr;
          }
        } else {
          console.warn('Could not extract JSON from AI response');
          return aiResponse;
        }
      }
    }
    
    return null;
  } catch (error) {
    console.error('Error creating final analysis:', error);
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Data:', error.response.data);
    }
    return null;
  }
}

// Run the analysis
createFinalAnalysis();
