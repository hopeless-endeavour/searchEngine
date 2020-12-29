const resultsBox = document.getElementById("results-box");

function addHtmlResults(results){
  clearResults();
  if (results.length == 0){
    bootbox.alert("No results found.")
  }
  var htmltoAppend = results.map((result) => {
   
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


function bookmark(id){
  console.log("bookmarked");
  var el = document.getElementById(id);
  if(el.hasClass("fa-bookmark-o")){
    // fetch request to _bookmark 
    // check if user logged in on backend 
    // if logged in change icon
    // add user id and article id to linked table in db
    // else flash that user must log in to bookmark 

     el.addClass("fa-bookmark").removeClass("fa-bookmark-o");
  } else{
    // remove article from users bookmarked pages 
    // remove user article link
    el.addClass("fa-bookmark-o").removeClass("fa-bookmark");
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
