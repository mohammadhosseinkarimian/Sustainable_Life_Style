import React, { useState } from 'react';
import axios from 'axios';

const FoodSpoilage = () => {
  const [result, setResult] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Preview Image
    setImagePreview(URL.createObjectURL(file));

    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await axios.post('http://127.0.0.1:5000/predict', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setResult(response.data.predicted_class);
      setConfidence((response.data.confidence * 100).toFixed(2));
    } catch (error) {
      console.error("Error fetching classification:", error);
    }
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '20px' }}>
      <h2>🍎 Food Spoilage Detector</h2>

      <input type="file" onChange={handleFileChange} style={{ marginBottom: '20px' }} />

      {imagePreview && (
        <div>
          <h4>Uploaded Image Preview:</h4>
          <img src={imagePreview} alt="Preview" style={{ width: '300px', marginBottom: '20px', borderRadius: '10px' }} />
        </div>
      )}

      {result && (
        <div style={{
          padding: '15px',
          borderRadius: '8px',
          backgroundColor: result === 'spoiled' ? '#ffcccc' : '#ccffcc',
          display: 'inline-block',
          marginTop: '20px',
          minWidth: '300px'
        }}>
          <h3 style={{ color: result === 'spoiled' ? 'red' : 'green' }}>
            {result === 'spoiled' ? '🚨 Spoiled Food Detected!' : '✅ Food is Edible!'}
          </h3>
          <p>Confidence: {confidence}%</p>
        </div>
      )}
    </div>
  );
};

export default FoodSpoilage;
