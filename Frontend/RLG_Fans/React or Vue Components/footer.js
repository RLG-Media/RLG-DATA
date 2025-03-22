// Footer.js

import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="footer mt-auto py-3 bg-dark text-light">
      <Container>
        <Row>
          {/* About Section */}
          <Col md={4}>
            <h5>About RLG Fans</h5>
            <p>
              RLG Fans is your comprehensive solution for content monetization, audience growth, and brand alignment.
              Stay on top of trends, increase engagement, and optimize for the best performance on every platform.
            </p>
          </Col>

          {/* Quick Links Section */}
          <Col md={4}>
            <h5>Quick Links</h5>
            <ul className="list-unstyled">
              <li><Link to="/dashboard" className="text-light">Dashboard</Link></li>
              <li><Link to="/analytics" className="text-light">Analytics</Link></li>
              <li><Link to="/projects" className="text-light">Projects</Link></li>
              <li><Link to="/settings" className="text-light">Settings</Link></li>
              <li><Link to="/help" className="text-light">Help & Support</Link></li>
            </ul>
          </Col>

          {/* Social Media Section */}
          <Col md={4}>
            <h5>Connect with Us</h5>
            <div className="social-icons">
              <a href="https://twitter.com/RLG_Fans" target="_blank" rel="noopener noreferrer">
                <i className="fab fa-twitter text-light mx-2"></i>
              </a>
              <a href="https://facebook.com/RLG_Fans" target="_blank" rel="noopener noreferrer">
                <i className="fab fa-facebook text-light mx-2"></i>
              </a>
              <a href="https://instagram.com/RLG_Fans" target="_blank" rel="noopener noreferrer">
                <i className="fab fa-instagram text-light mx-2"></i>
              </a>
              <a href="https://linkedin.com/company/RLG_Fans" target="_blank" rel="noopener noreferrer">
                <i className="fab fa-linkedin text-light mx-2"></i>
              </a>
            </div>
          </Col>
        </Row>

        {/* Footer Bottom Section */}
        <Row className="pt-3 border-top mt-3">
          <Col className="text-center">
            <p className="mb-0">&copy; {new Date().getFullYear()} RLG Fans. All rights reserved.</p>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

export default Footer;
