$(document).ready(function{
    var socket = io("/room", {transport: ['websocket']});



  socket.on('start_game', function(data){
    gridData = data.grid
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
  });

  socket.on('message', function(data){
    $('#log_window').append('<br>'+data)
  });

  $('#up').click(function(){
      text = 'up'
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

  socket.on('new_connection', function(data){
    $('#log_window').append('<li>'+data.connection+'</li>');
  });
  socket.on('new_disconnection', function(data){
    $('#log_window').append('<li>'+data.disconnection+'</li>');
  });
});
