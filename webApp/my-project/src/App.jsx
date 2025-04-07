import React, { useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from "react-router-dom";
import { FaHome, FaLeaf, FaShoppingCart, FaAppleAlt, FaEye, FaUser } from "react-icons/fa";
import FoodSpoilage from "./FoodSpoilage";
import Lifestyle from "./Lifestyle";
import Shopping from "./Shopping";
import "./App.css";

function Home() {
  return (
    <div>
      <h2>Welcome to the App! Please select a scanner from the menu above.</h2>
    </div>
  );
}

function ScannerPage({ title, endpoint }) {
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`http://localhost:5000/${endpoint}`)
      .then((res) => res.json())
      .then((data) => console.log(data))
      .catch((err) => console.error(err));
  }, [endpoint]);

  return (
    <div>
      <h2>{title} Scanner Launched</h2>
      <p>Please check the scanner window on the backend machine.</p>
      <button onClick={() => navigate("/")}>Return Home</button>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="app-wrapper">
        {/* TOP NAVBAR */}
        <header className="navbar">
          <div className="nav-content">
            <div className="nav-left">
              <Link to="/" className="nav-item">
                <FaHome /> Home
              </Link>
              <Link to="/lifestyle" className="nav-item">
                <FaLeaf /> Lifestyle
              </Link>
              <Link to="/grocery" className="nav-item">
                <FaShoppingCart /> Grocery
              </Link>
              <Link to="/food-spoilage" className="nav-item">
                <FaAppleAlt /> Food Spoilage
              </Link>
              <Link to="/object-detection" className="nav-item">
                <FaEye /> Object Detection
              </Link>
            </div>
            <div className="nav-right">
              <Link to="/signin" className="nav-item">
                <FaUser /> Sign In
              </Link>
            </div>
          </div>
        </header>

        <h1 className="page-title">🌿 Sustainable Lifestyle App</h1>
        <p className="subtitle">Empowering sustainability through smart AI detection</p>

        {/* 2x2 Grid Navigation */}
        <div className="grid-container">
          <Link to="/lifestyle" className="image-card fade-in">
            <img src="1.png" alt="Lifestyle" />
            <div className="image-text">Lifestyle</div>
          </Link>
          <Link to="/grocery" className="image-card fade-in">
            <img src="2.png" alt="Grocery" />
            <div className="image-text">Grocery</div>
          </Link>
          <Link to="/food-spoilage" className="image-card fade-in">
            <img src="3.png" alt="Food Spoilage" />
            <div className="image-text">Food Spoilage</div>
          </Link>
          <Link to="/object-detection" className="image-card fade-in">
            <img src="4.png" alt="Object Detection" />
            <div className="image-text">Object Detection</div>
          </Link>
        </div>

        {/* Routes */}
        <div className="content-wrapper">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/lifestyle" element={<ScannerPage title="Lifestyle" endpoint="lifestyle" />} />
            <Route path="/grocery" element={<ScannerPage title="Grocery" endpoint="grocery" />} />
            <Route path="/object-detection" element={<ScannerPage title="Object Detection" endpoint="object-detection" />} />
            <Route path="/food-spoilage" element={<h2>Food Spoilage Scanner not available.</h2>} />
            <Route path="/signin" element={<h2>Sign In Page (Not Implemented)</h2>} />
          </Routes>
        </div>

        {/* FOOTER */}
        <footer className="footer-bar">
          <div className="footer-icons">
            <a href="#" className="footer-icon" title="Instagram">
              <i className="fab fa-instagram"></i>
            </a>
            <a href="#" className="footer-icon" title="Twitter">
              <i className="fab fa-twitter"></i>
            </a>
            <a href="#" className="footer-icon" title="Email">
              <i className="fas fa-envelope"></i>
            </a>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
