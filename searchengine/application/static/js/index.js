

const resultsBox = document.getElementById("results-box");

function add_html_results(results) {
  // clear results before adding new results 
  clear_results();

  // convert results into html 
  var htmltoAppend = results[0].map((result) => {

    var user_id = document.getElementById('user_id');

    // if user is logged in display bookmark icon, otherwise don't display it 
    if (user_id == null) {
      var user_id = null;
      var button = '';
    } else {
      var user_id = user_id.innerHTML;
      var button = `<button id="${result.id}" class="btn bookmark-btn ml-auto" type="submit" onclick="bookmark(${result.id}, ${user_id})"><i class="fa fa-bookmark-o"></i></button>`
    };

    return `
    <div class="card">
      <div class="card-body">
        <div class="card-title d-flex flex-row">
        <a href="${window.origin}/view_article/${result.id}">
        <h5>${result.title}</h5>
        </a>
        <div class="card-cefr ml-auto p-2">${result.cefr}</div>
        ${button}
        </div>
        <a href="${result.url}" class="card-link card-subtitle text-muted">${result.url}</a>
        <p class="card-text">${result.text}...</p>
      </div>
    </div>
    `;
  }).join('');

  // add html results to results box 
  resultsBox.innerHTML = htmltoAppend;
}

function clear_results() {
  // loops through and removes all elements in results box 
  while (resultsBox.firstElementChild) {
    resultsBox.removeChild(resultsBox.firstElementChild);
  }
}

function create_body(type){
  // create body depending on the type of request
  if (type == "database") {
    var body = {
      type: type,
      query: document.getElementById("query").value,
      n: document.getElementById("n-select").value,
      filter_type: document.getElementById("filter-type").value,
      author: document.getElementById("author").value,
      level: document.getElementById("level").value
    };
  } else if (type == "current") {
    var body = {
      type: type,
      n: document.getElementById("n-select").value,
      domain: document.getElementById("domain").value
    };
  }
  return body;
}

function post_query(body) {
  // send post request to back end 
  fetch(`${window.origin}/_background`, {
    method: "POST",
    credentials: "include",
    body: JSON.stringify(body),
    cache: "no-cache",
    headers: new Headers({
      "content-type": "application/json"
    })
  })
    .then((response) => {
      if (response.status !== 200) {
        // catch if back end process failed 
        console.log(`Error. Status code: ${response.status}`);
        return;
      }
      response.json().then(function (data) {
        console.log(data);
        // checks if there are no results 
        if (data[0].length == 0) {
          alert("No results. Please try again with a different query.");
        }
        else {
          // calls function to render results 
          add_html_results(data);
        }
      });
    })
    .catch((error) => {
      // catch if request failed 
      console.log("Fetch error: " + error);
    });
}

function post_id(article_id, user_id, type) {

  // create body of request 
  var body = {
    'article_id': article_id,
    'user_id': user_id,
    'type': type
  };

  // send a post request to back end 
  fetch(`${window.origin}/_bookmark`, {
    method: "POST",
    credentials: "include",
    body: JSON.stringify(body),
    cache: "no-cache",
    headers: new Headers({
      "content-type": "application/json"
    })
  })
    .then((response) => {
      // catch if back end process failed 
      if (response.status !== 200) {
        console.log(`Error. Status code: ${response.status}`);
        return;
      }
      response.json().then(function (data) {
        // alert user of response of request
        alert(data["message"])
        console.log(data);
      });
    })
    .catch((error) => {
      // catch if request failed 
      console.log("Fetch error: " + error);
    });
}

function bookmark(article_id, user_id) {
  // get the article clicked by the user
  var el = document.getElementById(article_id);
  // get the bookmark icon
  var icon = el.childNodes[0]
  // if icon is white (bookark-o), post a "bookmark" type request 
  if (icon.className == "fa fa-bookmark-o") {
    post_id(article_id, user_id, "bookmark");
    // change icon to black
    icon.className = "fa fa-bookmark";
  } else {
    // icon is black, so post an "unbookmark" type request
    post_id(article_id, user_id, "unbookmark");
    // change icon to white
    if (window.location.pathname == "/bookmarks"){
      el.closest(".card").remove();
      set_num();
    }
    icon.className = "fa fa-bookmark-o";

  };
}

function translate_text(selectedtext) {
  console.log(selectedtext);
  var key = "AIzaSyAXK6vafPc4m5M7hPmLz8yvY5q9b7hb0Is";
  var url = "https://translation.googleapis.com/language/translate/v2?key=" + key;
  
  var body = {
    "source": "fr",
    "target": "en",
    "q": selectedtext
  }
  // send post request to google api 
  fetch(url, {
    method: "POST",
    body: JSON.stringify(body),
    cache: "no-cache",
    headers: new Headers({
      "content-type": "application/json"
    })
  })
    .then((response) => {
      // catch if back end process failed 
      if (response.status !== 200) {
        console.log(`Error. Status code: ${response.status}`);
        return;
      }
      response.json().then(function (data) {
        console.log(data.data.translations[0].translatedText);
        // alert user of the recieved transaltion 
        alert(`Translation: ${data.data.translations[0].translatedText}`);
        return;
      });
    })
    .catch((error) => {
      // catch if request failed 
      console.log("Fetch error: " + error);
      return;
    });
  }


function validate_db_query(body) {
  // if no filters and no query are selected alert user 
  if (body["query"] == '' && body["level"] == ''  && body["author"] == '' && (body["filter_type"] == ''| body["filter_type"] == 'relevance')){
    alert("Please fill in the search query and/or filters. ")
    return false;
  } else {
    return true;
  }

}

function validate_current_query(body) {
  // check that a domain is selected 
  if (body["domain"] == ''){
    alert("Please select a news site. ")
    return false;
  } else {
    return true;
  }

}

function set_num(){
  // function to dynamically update the text saying how many articles a user has bookmarked
   var num = document.getElementsByClassName("card").length - 1;
   document.getElementById("num").innerHTML = `You have ${num} bookmarked pages`;
}

$(function () {

  if (window.location.pathname == "/bookmarks"){
    set_num();
  }

  if (window.location.pathname.split("/")[1] == "view_article"){
    console.log("view");

    $("div").on("mouseup", () => {
      // get text selected by user and pass into translate functions 
      var selectedtext = document.getSelection().toString();
      if (selectedtext.length !== 0 || selectedtext.trim()) {  // ensure selected text isnt empty
        translate_text(selectedtext);
      }
    });
  }


  $("[name='submit1']").on('click', () => {
    var type = "database";
    console.log(type);
    var body = create_body(type);
    if (validate_db_query(body)){
      post_query(body);
    }
    return false;
  });

  $("[name='submit2']").on('click', () => {
    var type = "current";
    console.log(type);
    var body = create_body(type);
    if (validate_current_query(body)){
      post_query(body);
    }
    return false;
  });
});