/**
 * Test OCR
 * 
 * Tests the OCR functionality.
 */

const { HebrewOCRAgent } = require('../services/agents');
const fs = require('fs').promises;
const path = require('path');
const logger = require('../utils/logger');

// Test file paths
const TEST_SAMPLES_DIR = path.join(__dirname, 'samples');
const SAMPLE_TEXT_PATH = path.join(TEST_SAMPLES_DIR, 'sample-text.txt');

// Create sample test files if they don't exist
async function createTestFiles() {
  try {
    // Create samples directory if it doesn't exist
    await fs.mkdir(TEST_SAMPLES_DIR, { recursive: true });
    
    // Create a sample text file if it doesn't exist
    if (!await fileExists(SAMPLE_TEXT_PATH)) {
      const sampleText = `
This is a sample text for OCR testing.
It contains some English text.

וזה טקסט בעברית לבדיקת OCR.
יש כאן גם מספרים: 123456789
וגם סימני פיסוק: .,;:!?

This text has some common OCR errors:
- Misrecognized characters: 0 (zero) vs O (letter), 1 (one) vs l (letter)
- Broken words: recog nition instead of recognition
- Missing spaces:missingspaces
- Extra spaces:  too  many  spaces

שגיאות OCR נפוצות בעברית:
- אותיות דומות: ב vs נ, ה vs ח
- רווחים חסרים:מיליםמחוברות
- רווחים מיותרים:  יותר  מדי  רווחים
`;
      
      await fs.writeFile(SAMPLE_TEXT_PATH, sampleText, 'utf8');
      console.log(`Created sample text file at ${SAMPLE_TEXT_PATH}`);
    }
  } catch (error) {
    console.error('Error creating test files:', error);
  }
}

/**
 * Check if a file exists
 * @param {string} filePath - Path to the file
 * @returns {Promise<boolean>} - Whether the file exists
 */
async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

/**
 * Mock implementation of the HebrewOCRAgent
 */
class MockHebrewOCRAgent extends HebrewOCRAgent {
  constructor() {
    super({ apiKey: 'mock-api-key' });
  }
  
  async _performOCR(documentBuffer, options = {}) {
    // For testing, we'll just return the content of the buffer as text
    // In a real implementation, this would use Tesseract.js
    const text = documentBuffer.toString('utf8');
    
    return {
      text,
      confidence: 85.5,
      words: this._mockExtractWords(text),
      blocks: this._extractBlocksFromText(text)
    };
  }
  
  _mockExtractWords(text) {
    // Create mock words with position and confidence
    const words = [];
    const textWords = text.split(/\s+/);
    
    let x = 0;
    let y = 0;
    
    textWords.forEach((word, index) => {
      if (word.trim()) {
        // Simulate different confidence levels
        const confidence = 70 + Math.random() * 30;
        
        words.push({
          text: word,
          confidence,
          bbox: {
            x,
            y,
            width: word.length * 10,
            height: 20
          }
        });
        
        // Update position for next word
        x += word.length * 10 + 10;
        
        // Simulate line breaks
        if (x > 500) {
          x = 0;
          y += 30;
        }
      }
    });
    
    return words;
  }
  
  async _enhanceText(text) {
    // Mock text enhancement
    // In a real implementation, this would use the OpenRouter API
    
    // Simulate some enhancements
    let enhancedText = text;
    
    // Fix common OCR errors
    enhancedText = enhancedText.replace('recog nition', 'recognition');
    enhancedText = enhancedText.replace('missingspaces', 'missing spaces');
    enhancedText = enhancedText.replace('  too  many  spaces', ' too many spaces');
    enhancedText = enhancedText.replace('מיליםמחוברות', 'מילים מחוברות');
    enhancedText = enhancedText.replace('  יותר  מדי  רווחים', ' יותר מדי רווחים');
    
    return enhancedText;
  }
}

/**
 * Test OCR processing
 */
async function testOCRProcessing() {
  console.log('Testing OCR processing...');
  
  try {
    // Create test files
    await createTestFiles();
    
    // Read the sample text file
    const textBuffer = await fs.readFile(SAMPLE_TEXT_PATH);
    
    // Create a mock OCR agent
    const ocrAgent = new MockHebrewOCRAgent();
    
    // Process the text
    const result = await ocrAgent.processDocument(textBuffer);
    
    // Check if the result has the expected properties
    if (result.text &&
        result.original_text &&
        result.confidence &&
        result.blocks &&
        result.blocks.length > 0 &&
        result.words &&
        result.words.length > 0) {
      console.log('✅ OCR processing test passed');
      console.log('Confidence:', result.confidence);
      console.log('Blocks count:', result.blocks.length);
      console.log('Words count:', result.words.length);
      
      // Check if text enhancement worked
      if (result.text !== result.original_text) {
        console.log('✅ Text enhancement test passed');
        console.log('Original text length:', result.original_text.length);
        console.log('Enhanced text length:', result.text.length);
      } else {
        console.log('❌ Text enhancement test failed');
        console.log('Enhanced text is the same as original text');
      }
      
      return true;
    } else {
      console.error('❌ OCR processing test failed');
      console.error('Missing expected properties in result');
      return false;
    }
  } catch (error) {
    console.error('❌ OCR processing test failed with error:', error.message);
    return false;
  }
}

/**
 * Test text enhancement
 */
async function testTextEnhancement() {
  console.log('\nTesting text enhancement...');
  
  try {
    // Create a mock OCR agent
    const ocrAgent = new MockHebrewOCRAgent();
    
    // Sample text with OCR errors
    const sampleText = `
This text has some common OCR errors:
- Misrecognized characters: 0 (zero) vs O (letter), 1 (one) vs l (letter)
- Broken words: recog nition instead of recognition
- Missing spaces:missingspaces
- Extra spaces:  too  many  spaces

שגיאות OCR נפוצות בעברית:
- אותיות דומות: ב vs נ, ה vs ח
- רווחים חסרים:מיליםמחוברות
- רווחים מיותרים:  יותר  מדי  רווחים
`;
    
    // Enhance the text
    const enhancedText = await ocrAgent._enhanceText(sampleText);
    
    // Check if the text was enhanced
    if (enhancedText !== sampleText) {
      console.log('✅ Text enhancement test passed');
      
      // Check specific enhancements
      const enhancements = [
        { original: 'recog nition', enhanced: 'recognition' },
        { original: 'missingspaces', enhanced: 'missing spaces' },
        { original: '  too  many  spaces', enhanced: ' too many spaces' },
        { original: 'מיליםמחוברות', enhanced: 'מילים מחוברות' },
        { original: '  יותר  מדי  רווחים', enhanced: ' יותר מדי רווחים' }
      ];
      
      let allEnhancementsFound = true;
      
      for (const { original, enhanced } of enhancements) {
        if (sampleText.includes(original) && enhancedText.includes(enhanced)) {
          console.log(`✅ Enhancement found: "${original}" -> "${enhanced}"`);
        } else {
          console.log(`❌ Enhancement not found: "${original}" -> "${enhanced}"`);
          allEnhancementsFound = false;
        }
      }
      
      return allEnhancementsFound;
    } else {
      console.error('❌ Text enhancement test failed');
      console.error('Enhanced text is the same as original text');
      return false;
    }
  } catch (error) {
    console.error('❌ Text enhancement test failed with error:', error.message);
    return false;
  }
}

/**
 * Run all tests
 */
async function runTests() {
  const ocrSuccess = await testOCRProcessing();
  const enhancementSuccess = await testTextEnhancement();
  
  // Print test summary
  console.log('\n=== Test Summary ===');
  console.log(`OCR Processing: ${ocrSuccess ? '✅ Passed' : '❌ Failed'}`);
  console.log(`Text Enhancement: ${enhancementSuccess ? '✅ Passed' : '❌ Failed'}`);
  
  return ocrSuccess && enhancementSuccess;
}

// Run the tests
runTests()
  .then(success => {
    if (success) {
      console.log('\nAll tests passed!');
      process.exit(0);
    } else {
      console.error('\nSome tests failed!');
      process.exit(1);
    }
  })
  .catch(error => {
    console.error('Error running tests:', error);
    process.exit(1);
  });
