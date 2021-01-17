const resultsBox = document.getElementById("results-box");

function add_html_results(results) {
  clear_results();

  var htmltoAppend = results[0].map((result) => {

    var user_id = document.getElementById('user_id');

    if (user_id == null) {
      var user_id = null;
      var button = '';
    } else {
      var user_id = user_id.innerHTML;
      var button = `<button id="${result.id}" class="btn bookmark-btn ml-auto" type="submit" onclick="bookmark(${result.id}, ${user_id})"><i class="fa fa-bookmark-o"></i></button>`
    };

    return `
    <div class="card">
      <div class="card-header">
         CEFR: ${result.cefr}
       </div>
      <div class="card-body">
        <div class="card-title d-flex flex-row">
        <a href="${window.origin}/view_article/${result.id}"><h5>${result.title}</h5></a>
        ${button}
        </div>
        <a href="${result.url}" class="card-link card-subtitle text-muted">${result.url}</a>
        <p class="card-text">${result.text}...</p>
      </div>
    </div>
    `;
  }).join('');
  resultsBox.innerHTML = htmltoAppend;
}

function clear_results() {
  while (resultsBox.firstElementChild) {
    resultsBox.removeChild(resultsBox.firstElementChild);
  }
}

function load_results() {
  var query = document.getElementById("query");
  var n = document.getElementById("n-select");
  var filter_type = document.getElementById("filter-type");
  var level = document.getElementById("level");
  var domain = document.getElementById("domain");

  var entry = {
    query: query.value,
    n: n.value,
    filter_type: filter_type.value,
    level: level.value,
    domain: domain.value
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
        if (data[0].length == 0){
          alert("No results. Please try again with a different query.");
        }
        else {add_html_results(data);
        }
      });
    })
    .catch((error) => {
      console.log("Fetch error: " + error);
    });
}

function setBackground() {
  fetch(`${window.origin}/_upload`)
    .then(response => response.json())
    .then(data => {
      console.log(data);
      document.body.style.backgroundImage = `url(${data})`;
    })
}

function post_id(article_id, user_id, type) {

  var entry = {
    'article_id': article_id,
    'user_id': user_id,
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

function bookmark(article_id, user_id) {
  var el = document.getElementById(article_id);
  var icon = el.childNodes[0]
  console.log(user_id);
  if (icon.className == "fa fa-bookmark-o") {
    post_id(article_id, user_id, "bookmark");
    icon.className = "fa fa-bookmark";
  } else {
    post_id(article_id, user_id, "unbookmark");
    icon.className = "fa fa-bookmark-o";
  };
}

function translate_text() {
  var textarea = document.getElementsByTagName('p');
  var selectedtext = '';

  if (document.getSelection) {
    selectedtext = document.getSelection().toString();
    console.log(selectedtext);
    // post request to translation api 
    // render results 
    }
  else return;

}

$(function () {

  // setBackground();

  $('.input-daterange').datepicker({
    format: 'dd-mm-yyyy',
    autoclose: true,
    clearBtn: true,
    disableTouchKeyboard: true
  });

  // var collapseElementList = [].slice.call(document.querySelectorAll('.collapse'))
  // var collapseList = collapseElementList.map(function (collapseEl) {
  //   return new bootstrap.Collapse(collapseEl)
  // })


  $("#submit-btn").on('click', () => {
    load_results();
    return false;
  });
});
