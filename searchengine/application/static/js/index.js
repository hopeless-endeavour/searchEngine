const resultsBox = document.getElementById("results-box");

function addHtmlResults(results){
  clearResults();
  if (results.length == 0){
    bootbox.alert("No results found.")
  }
  var htmltoAppend = results[0].map((result) => {
   
    return `
    <div class="card">
      <div class="card-body">
        <div class="card-title d-flex flex-row">
        <h5>${result.title}</h5>
        <button id="${result.id}" class="btn bookmark-btn ml-auto" type="submit" onclick="bookmark(${result.id})"><i class="fa fa-bookmark-o"></i></button>
        </div>
        <a href="${result.url}" class="card-link card-subtitle text-muted">${result.url}</a>
        <p class="card-text">${result.text}...</p>
      </div>
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


  fetch(`${window.origin}/_background`, {
    method: "POST",
    credentials: "include",
    body: JSON.stringify(entry),
    cache: "no-cache",
    headers: new Headers({
      "content-type": "application/json"
    })
  })
  .then((response) => {
      if (response.status !== 200) {
        console.log(`Error. Status code: ${response.status}`);
        return;
      }
      response.json().then(function (data) {
        console.log(data);
        addHtmlResults(data);
      });
    })
  .catch((error) => {
      console.log("Fetch error: " + error);
    });
}

function setBackground(){
  fetch(`${window.origin}/_upload`)
  .then(response => response.json())
  .then(data => {
    console.log(data);
    document.body.style.backgroundImage = `url(${data})`;
  })  
}

function post_id(id, type){
  
  var entry = {
    'id': id,
    'type': type
  };

  fetch(`${window.origin}/_bookmark`, {
    method: "POST",
    credentials: "include",
    body: JSON.stringify(entry),
    cache: "no-cache",
    headers: new Headers({
      "content-type": "application/json"
    })
  })
  .then((response) => {
      if (response.status !== 200) {
        console.log(`Error. Status code: ${response.status}`);
        return;
      }
      response.json().then(function (data) {
        console.log(data);
      });
    })
  .catch((error) => {
      console.log("Fetch error: " + error);
    });
}

function bookmark(id){
  var el = document.getElementById(id);
  var icon = el.childNodes[0]
  if(icon.className == "fa fa-bookmark-o"){
    post_id(id, "bookmark");
    icon.className = "fa fa-bookmark";
  } else{
    post_id(id, "unbookmark");
    icon.className ="fa fa-bookmark-o";
  };
}

$(function(){

  setBackground();

  $('.input-daterange').datepicker({
    format: 'dd-mm-yyyy',
    autoclose: true,
    clearBtn: true,
    disableTouchKeyboard: true
    });

  $("#submit-btn").on('click', () => {
    loadResults();
    return false;
    });

});
