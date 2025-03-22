// ui_tests.js
// Cypress end-to-end tests for the RLG Data and RLG Fans interfaces

describe('RLG Data and RLG Fans UI Tests', () => {

    // Base URLs for RLG Data and RLG Fans
    const BASE_URL_RLG_DATA = 'http://localhost:5000';
    const BASE_URL_RLG_FANS = 'http://localhost:5001';
  
    // Helper function to perform login
    function login(username, password, baseUrl) {
      cy.visit(`${baseUrl}/login`);
      cy.get('input[name="username"]').type(username);
      cy.get('input[name="password"]').type(password);
      cy.get('button[type="submit"]').click();
    }
  
    // Test Suite for RLG Data
    describe('RLG Data UI Tests', () => {
      beforeEach(() => {
        login('testuser', 'password123', BASE_URL_RLG_DATA);
      });
  
      it('Should display the RLG Data dashboard correctly', () => {
        cy.visit(`${BASE_URL_RLG_DATA}/dashboard`);
        cy.get('h1').contains('RLG Data Dashboard').should('be.visible');
        cy.get('.chart-container').should('exist');
        cy.get('.data-table').should('exist');
      });
  
      it('Should allow navigation through the sidebar', () => {
        cy.get('.sidebar a').contains('Dashboard').click();
        cy.url().should('include', '/dashboard');
        cy.get('.sidebar a').contains('Reports').click();
        cy.url().should('include', '/reports');
        cy.get('.sidebar a').contains('Settings').click();
        cy.url().should('include', '/settings');
      });
  
      it('Should render charts and tables with data', () => {
        cy.get('.chart-container').should('be.visible');
        cy.get('.data-table').should('be.visible');
        cy.get('.data-table tbody tr').should('have.length.greaterThan', 0);
      });
    });
  
    // Test Suite for RLG Fans
    describe('RLG Fans UI Tests', () => {
      beforeEach(() => {
        login('testuser', 'password123', BASE_URL_RLG_FANS);
      });
  
      it('Should display the RLG Fans dashboard correctly', () => {
        cy.visit(`${BASE_URL_RLG_FANS}/dashboard`);
        cy.get('h1').contains('RLG Fans Dashboard').should('be.visible');
        cy.get('.chart-container').should('exist');
        cy.get('.data-table').should('exist');
      });
  
      it('Should allow interaction with RLG Fans features', () => {
        cy.get('.sidebar a').contains('OnlyFans Analysis').click();
        cy.url().should('include', '/onlyfans');
        cy.get('.sidebar a').contains('Patreon Analysis').click();
        cy.url().should('include', '/patreon');
      });
  
      it('Should load analytics and display data in tables', () => {
        cy.visit(`${BASE_URL_RLG_FANS}/analytics`);
        cy.get('.analytics-section').should('be.visible');
        cy.get('.chart-container').should('exist');
        cy.get('.data-table').should('exist');
      });
    });
  
    // Test cross-tool navigation between RLG Data and RLG Fans
    describe('Cross-Tool Navigation Tests', () => {
      it('Should allow users to switch between RLG Data and RLG Fans', () => {
        login('testuser', 'password123', BASE_URL_RLG_DATA);
        cy.get('.navbar a').contains('Switch to RLG Fans').click();
        cy.url().should('include', BASE_URL_RLG_FANS);
  
        login('testuser', 'password123', BASE_URL_RLG_FANS);
        cy.get('.navbar a').contains('Switch to RLG Data').click();
        cy.url().should('include', BASE_URL_RLG_DATA);
      });
    });
  
    // Test for responsive UI elements
    describe('Responsive Design Tests', () => {
      it('Should display mobile-friendly layout on smaller screens', () => {
        cy.viewport('iphone-6');
        cy.visit(`${BASE_URL_RLG_DATA}/dashboard`);
        cy.get('.sidebar').should('not.be.visible');
        cy.get('.navbar').should('be.visible');
      });
  
      it('Should display desktop layout on larger screens', () => {
        cy.viewport('macbook-15');
        cy.visit(`${BASE_URL_RLG_FANS}/dashboard`);
        cy.get('.sidebar').should('be.visible');
        cy.get('.main-content').should('be.visible');
      });
    });
  });
  