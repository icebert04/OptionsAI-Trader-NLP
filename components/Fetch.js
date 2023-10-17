import axios from 'axios';
import React, { useState } from 'react';

const apiUrl = 'http://localhost:5000/api/analyze';

function YourComponent() {
  const [isLoading, setIsLoading] = useState(false);
  const [text, setText] = useState('');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [namedEntities, setNamedEntities] = useState(null);

  // Add a state to track the uploaded file
  const [uploadedFile, setUploadedFile] = useState(null);

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  // Update handleFileUpload to set the uploaded file
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    setUploadedFile(file);
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      console.log("Text:", text);
      console.log("Uploaded File:", uploadedFile);
  
      let formData = new FormData();
  
      // Always append the text to the FormData
      formData.append('text', text);
  
      // Check if a file is uploaded
      if (uploadedFile) {
        // Extract text from the PDF file here
        formData.append('file', uploadedFile);
      }
  
      console.log("FormData for submission:", formData);
  
      // Clear previous analysis results here
      setAnalysisResults(null);
      setNamedEntities(null);
  
      const response = await axios.post(apiUrl, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
  
      const data = response.data;
      setAnalysisResults(data);
      setNamedEntities(data.named_entities);
  
      // Reset text and uploadedFile to null after analysis
      setText('');
      setUploadedFile(null);
    } catch (error) {
      console.error('Error analyzing text:', error);
    }
    setIsLoading(false);
  };
  
  return (
    <div className="bg-gray-100 min-h-screen py-8">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
        {isLoading ? (
          <p>Loading...</p>
        ) : (
          <>
            <TextAnalysisForm setText={setText} handleFileUpload={handleFileUpload} />
            <button
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              onClick={handleSubmit}
            >
              Analyze
            </button>
            {analysisResults && (
                <div className='mb-4'>
                <h2 className="text-xl font-semibold mb-2">Analysis Results:</h2>
                <ul>
                  <li><b>Detected Events:</b> {analysisResults.detected_events.join(', ')}</li>
                  <li><b>Sentiment:</b> {analysisResults.sentiment}</li>
                  <li><b>Risk Level:</b> {analysisResults.risk_level}</li>
                  <li><b>Volatility Mentions:</b></li>
                  <ul>
                    {analysisResults.volatility_mentions.map((mention, index) => (
                      <li key={index}>{mention}</li>
                    ))}
                  </ul>
                  {analysisResults && analysisResults.m_and_a_info && (
                    <div className="mb-4">
                      <h2 className="text-xl font-semibold mb-2">M&A Information:</h2>
                      <ul>
                        {analysisResults.m_and_a_info.map((mAndA, index) => (
                          <li key={index}>
                            <p className='pb-4'>
                              {mAndA.split(/(\s|;|\.)/).map((word, wordIndex) => {
                                // Define your M&A-related keywords here
                                const keywords = ["Merger", "Acquisition", "Banking sector", "Pakistan", "Event study"];
                                if (keywords.includes(word.trim())) {
                                  // Apply formatting to keywords (e.g., bold)
                                  return <strong key={wordIndex}>{word}</strong>;
                                } else {
                                  return <span key={wordIndex}>{word}</span>;
                                }
                              })}
                            </p>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
              <br/>
                  <ul>
                    {Object.entries(analysisResults.event_sentences).map(
                      ([event, sentences], index) => (
                        <li key={index}>
                          <strong>{event}:</strong>
                          <ul>
                            {sentences.map((sentence, sIndex) => (
                              <li key={sIndex}>{sentence}</li>
                            ))}
                          </ul>
                        </li>
                      )
                    )}
                  </ul>
                </ul>
              </div>
            )}
            <br/>
            {namedEntities && (
              <div>
                <h1 className='text-lg'><b>Named Entities:</b></h1>
                {Object.entries(namedEntities).map(([sentence, entities], index) => (
                  <div key={index} className='pb-3 border-y-2'>
                    <h3>Sentence:</h3>
                    <p>{sentence}</p>
                    <h3>Named Entities:</h3>
                    <ul>
                      {entities.map((entity, entityIndex) => (
                        <li key={entityIndex}>
                          <strong>Text:</strong> {entity.text}, <strong>Label:</strong> {entity.label}
                          {entity.label_explanation && (
                            <span>, <strong>Label Explanation:</strong> {entity.label_explanation}</span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function TextAnalysisForm({ setText, handleFileUpload }) {
  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  return (
    <div className="mb-4">
      <form>
        <textarea
          rows="4"
          cols="50"
          onChange={handleTextChange}
          placeholder="Enter or paste text here"
          className="w-full p-2 border rounded"
        />
        <input
          type="file"
          accept=".txt, .pdf, .csv, .xlsx"
          onChange={handleFileUpload}
        />
      </form>
    </div>
  );
}

export default YourComponent;
