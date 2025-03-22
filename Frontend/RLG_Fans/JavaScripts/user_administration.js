/**
 * user_administration.js
 *
 * This script enhances the user administration page with interactive features
 * such as AJAX deletion of user accounts and dynamic search filtering.
 *
 * Features:
 * - Intercepts delete form submissions to perform an AJAX request, confirming deletion.
 * - Dynamically filters the user table based on the search input.
 * - Logs errors and provides user feedback.
 *
 * Recommendations:
 * - For large user lists, add pagination and sorting functionality.
 * - Replace alert dialogs with custom modals or toast notifications for improved UX.
 * - Ensure that server-side endpoints are secured (including CSRF protection).
 */

document.addEventListener("DOMContentLoaded", () => {
    // ------------------------------------------------------
    // AJAX Deletion of Users
    // ------------------------------------------------------
    // Find all forms that are used for deletion. We assume that the action URL contains '/delete'
    // and that these forms are located within the user administration table.
    const deleteForms = document.querySelectorAll("form[action*='/delete']");
    deleteForms.forEach(form => {
      form.addEventListener("submit", async (e) => {
        // Prevent the default form submission behavior.
        e.preventDefault();
        
        // Display a confirmation dialog.
        const confirmed = confirm("Are you sure you want to delete this user?");
        if (!confirmed) return;
        
        // Get the action URL from the form.
        const actionUrl = form.getAttribute("action");
        
        try {
          // Send an asynchronous POST request to delete the user.
          const response = await fetch(actionUrl, {
            method: "POST",
            credentials: "same-origin",
            headers: {
              "X-Requested-With": "XMLHttpRequest"
              // Optionally, include a CSRF token header if your backend requires it.
            }
          });
          
          // Check the response status.
          if (response.ok) {
            // If deletion is successful, remove the corresponding table row.
            const row = form.closest("tr");
            if (row) row.remove();
            alert("User deleted successfully.");
          } else {
            console.error(`Error deleting user: ${response.statusText}`);
            alert("Error deleting user.");
          }
        } catch (error) {
          console.error("Error during deletion AJAX call:", error);
          alert("Error deleting user.");
        }
      });
    });
    
    // ------------------------------------------------------
    // Dynamic Search Filtering for User Table
    // ------------------------------------------------------
    // If a search input exists (with the ID "userSearch"), attach a keyup event listener
    // to filter the table rows based on the username.
    const searchInput = document.getElementById("userSearch");
    if (searchInput) {
      searchInput.addEventListener("keyup", () => {
        const filter = searchInput.value.toLowerCase();
        const tableRows = document.querySelectorAll("table tbody tr");
        
        tableRows.forEach(row => {
          // Assume that the second cell (index 1) contains the username.
          const usernameCell = row.querySelector("td:nth-child(2)");
          if (usernameCell) {
            const usernameText = usernameCell.textContent.toLowerCase();
            // Display the row if the username contains the filter text; hide it otherwise.
            row.style.display = usernameText.indexOf(filter) > -1 ? "" : "none";
          }
        });
      });
    }
    
    // ------------------------------------------------------
    // Additional Functionality: Region Filtering (Optional)
    // ------------------------------------------------------
    // If you have a region filter dropdown (with ID "regionFilter"), you could add an event listener
    // to filter the table rows by region. For example:
    /*
    const regionFilter = document.getElementById("regionFilter");
    if (regionFilter) {
      regionFilter.addEventListener("change", () => {
        const selectedRegion = regionFilter.value.toLowerCase();
        const tableRows = document.querySelectorAll("table tbody tr");
        
        tableRows.forEach(row => {
          const regionCell = row.querySelector("td:nth-child(4)"); // Assuming the 4th column is Region.
          if (regionCell) {
            const regionText = regionCell.textContent.toLowerCase();
            row.style.display = regionText === selectedRegion || selectedRegion === "all" ? "" : "none";
          }
        });
      });
    }
    */
  });
  