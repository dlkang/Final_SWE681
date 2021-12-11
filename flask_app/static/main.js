var socket = io()
socket.on('connect', function() {
    socket.emmit('my event', {data:'Im connected!'})
})


function get_grid(){
    return graphData;
}

gridData = get_grid();
console.log(gridData)

var grid = d3.select("#grid")
	.append("svg")
	.attr("width","510px")
	.attr("height","510px");

var row = grid.selectAll(".row")
	.data(gridData)
	.enter().append("g")
	.attr("class", "row");

var column = row.selectAll(".square")
	.data(function(d) { return d; })
	.enter().append("rect")
	.attr("class","square")
	.attr("x", function(d) { return d.x; })
	.attr("y", function(d) { return d.y; })
	.attr("width", function(d) { return d.width; })
	.attr("height", function(d) { return d.height; })
	.attr("fill", function(d) {
	    return (d.hero > 0) ? "#0000ff" : "#fff";
	})
	.attr("stroke", "#222")


$("button").click(function(){
    var direction = $(this).val();
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "checkmove");
    xhttp.send(direction);
});


  $('#up').click(function(){
      jsonToSend = {bid: myBid, see: false};
      socket.emit('client_game_turn',jsonToSend);
  });
  $('#down').click(function(){
      jsonToSend = {bid: myBid, see: false};
      socket.emit('client_game_turn',jsonToSend);
  });
  $('#left').click(function(){
      jsonToSend = {bid: myBid, see: false};
      socket.emit('client_game_turn',jsonToSend);
  });
  $('#right').click(function(){
      jsonToSend = {bid: myBid, see: false};
      socket.emit('client_game_turn',jsonToSend);
  });
  $('#attack').click(function(){
      jsonToSend = {bid: myBid, see: false};
      socket.emit('client_game_turn',jsonToSend);
  });



/**
var paragraph = document.getElementById("log_window");
var text = document.createTextNode(info);
paragraph.appendChild(text)
var info = {{info | safe}} **/