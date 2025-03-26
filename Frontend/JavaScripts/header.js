// Header.js

import React from 'react';
import { Navbar, Nav, Container, NavDropdown } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <header>
      <Navbar bg="dark" variant="dark" expand="lg" collapseOnSelect>
        <Container>
          {/* Brand Logo */}
          <LinkContainer to="/dashboard">
            <Navbar.Brand>RLG Fans</Navbar.Brand>
          </LinkContainer>

          {/* Toggler for mobile view */}
          <Navbar.Toggle aria-controls="basic-navbar-nav" />

          {/* Navigation Links */}
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <LinkContainer to="/dashboard">
                <Nav.Link>Dashboard</Nav.Link>
              </LinkContainer>
              <LinkContainer to="/analytics">
                <Nav.Link>Analytics</Nav.Link>
              </LinkContainer>
              <LinkContainer to="/projects">
                <Nav.Link>Projects</Nav.Link>
              </LinkContainer>
              <LinkContainer to="/settings">
                <Nav.Link>Settings</Nav.Link>
              </LinkContainer>
              <LinkContainer to="/help">
                <Nav.Link>Help</Nav.Link>
              </LinkContainer>
            </Nav>

            {/* User Dropdown */}
            <Nav>
              <NavDropdown title="Profile" id="user-nav-dropdown" align="end">
                <LinkContainer to="/profile">
                  <NavDropdown.Item>My Profile</NavDropdown.Item>
                </LinkContainer>
                <NavDropdown.Divider />
                <NavDropdown.Item onClick={handleLogout}>Logout</NavDropdown.Item>
              </NavDropdown>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
    </header>
  );
};

export default Header;
