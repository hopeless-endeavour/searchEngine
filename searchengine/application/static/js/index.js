const resultsBox = document.getElementById("results-box");

function addHtmlResults(results){
  clearResults();
  if (results.length == 0){
    bootbox.alert("No results found.")
  }
  var htmltoAppend = results.map((result) => {
    return `
    <div class="card"><div class="card-body">
        <h5 class="card-title">${result.title}</h5>
        <a href="#" class="card-link card-subtitle text-muted">${result.url}</a>
        <p class="card-text">${result.text}</p></div>
    </div>
    `;
  }).join('');
  resultsBox.innerHTML = htmltoAppend;
}

function clearResults(){
  while (resultsBox.firstElementChild){
    resultsBox.removeChild(resultsBox.firstElementChild);
  }
}

function loadResults(){
  var query = document.getElementById("query");
  var n = document.getElementById("n-select");

  var entry = {
      query: query.value,
      n: n.value
  };

  // document.getElementById("submit-btn").disabled = true;

  fetch(`${window.origin}/_background`, {
    method: "POST",
    credentials: "include",
    body: JSON.stringify(entry),
    cache: "no-cache",
    headers: new Headers({
      "content-type": "application/json"
    })
  })
  .then(function(response) {
    if (response.status !== 200) {
      console.log(`Error. Status code: ${response.status}`);
      return;
    }
    response.json().then(function(data) {
      console.log(data);
      addHtmlResults(data)
    });
  })
  .catch(function(error) {
    console.log("Fetch error: " + error);
  });
}


$(function(){
  $("#submit-btn").bind('click', (event) => {
    loadResults();
    return false;
  });
});
