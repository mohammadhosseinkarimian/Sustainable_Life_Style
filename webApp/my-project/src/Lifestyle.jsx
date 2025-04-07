import React, { useState } from 'react';
import axios from 'axios';

const Lifestyle = () => {
  const [lightStatus, setLightStatus] = useState(null);
  const [brightness, setBrightness] = useState(null);
  const [feedback, setFeedback] = useState(null);

  const handleScan = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/scan-light');
      setLightStatus(response.data.light_status);
      setBrightness(response.data.brightness);
      setFeedback(response.data.feedback);
    } catch (error) {
      console.error("Error scanning light:", error);
    }
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '20px' }}>
      <h2>💡 Sustainable Lifestyle Assistant</h2>
      <button onClick={handleScan} style={{ padding: '10px 20px', marginTop: '20px' }}>
        Scan Room for Light Status
      </button>

      {lightStatus && (
        <div style={{
          padding: '15px',
          marginTop: '20px',
          backgroundColor: lightStatus === "ON" ? '#ffcccc' : '#ccffcc',
          borderRadius: '10px',
          display: 'inline-block'
        }}>
          <h3>Light Status: {lightStatus}</h3>
          <p>Brightness Level: {brightness}</p>
          <p>{feedback}</p>
        </div>
      )}
    </div>
  );
};

export default Lifestyle;
