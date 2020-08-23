$(function(){
  $("#submit-btn").bind('click', function() {
    var query = document.getElementById("query");
    var n = document.getElementById("n-select");
    var line = document.createElement("p");

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
    .then(function(response) {
      if (response.status !== 200) {
        console.log(`Looks like there was a problem. Status code: ${response.status}`);
        return;
      }
      response.json().then(function(data) {
        console.log(data);
        document.getElementById("results-box").innerHTML = data;
        // line.innerHTML = "<strong>" + data.query + ": </strong>";
        // document.getElementById("results-box").append(line);
      });
    })
    .catch(function(error) {
      console.log("Fetch error: " + error);
  });
  });
});
