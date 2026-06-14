document.addEventListener("DOMContentLoaded", function() {
  const input = document.getElementById("guess-input");
  const suggestionBox = document.getElementById("autocomplete-list");
  const form = document.getElementById("guess-form");
  const autocompleteUrl = form.getAttribute("data-autocomplete-url");

  input.addEventListener("input", function() {
    const query = this.value;
    
    if (query.length < 2) {
      suggestionBox.innerHTML = "";
      return;
    }

    // Use the URL we extracted from the form
    fetch(`${autocompleteUrl}?q=${encodeURIComponent(query)}`)
      .then(response => response.json())
      .then(data => { // Wipe out old suggestions
        suggestionBox.innerHTML = ""; 

        // Build the dropdown
        data.suggestions.forEach(title => {
          const item = document.createElement("div");
          item.innerHTML = title;
          
          // Make them clickable
          item.addEventListener("click", function() {
            input.value = title;
            suggestionBox.innerHTML = "";
          });
          
          suggestionBox.appendChild(item);
        });
      })
      .catch(error => console.error('Error fetching suggestions:', error));
  });

  // Click anywhere else to close the input box
  document.addEventListener("click", function (e) {
    if (e.target !== input) {
      suggestionBox.innerHTML = "";
    }
  });
});