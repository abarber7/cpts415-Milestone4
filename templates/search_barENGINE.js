// function to fetch suggestions from the backend API
async function fetchSuggestions() 
{
    // gets value of the text in the search box
    const query = document.getElementById('searchBox').value;
    if (query.length > 0) 
    {
        // the '\autofill' endpoint expects a query parameter 'query'
        // conversion of json format for suggestion needed
        try
        {
        const response = await fetch(`/autofill?query=${query}`);
        const suggestions = await response.json();
        displaySuggestions(suggestions); // display suggestions
        }
        catch (error)
        {
            console.error("Error fetching suggestions.")
        }
    }
    else 
    {
        // is the search box is empty, clears the list of suggestions.
        clearSuggestions();
    }
}

// UI display of the suggestions (in drop-down list)
function displaySuggestions(suggestions) 
{
    // gets suggestion list
    const suggestionsList = document.getElementById('suggestionsList');
    suggestionsList.innerHTML = ''; // clear previous suggestions

    // looping through of the suggestions returned from API
    suggestions.forEach(suggestion => {

        // create new list item for each suggestion 
        const listItem = document.createElement('listItem');

        // setting the text of content of the list item to the suggestion   
        listItem.textContent = suggestion;
        suggestionsList.appendChild(listItem);
    });
}

// clears the suggestion list
function clearSuggestions() {
    document.getElementById('suggestionsList').innerHTML = '';
}
