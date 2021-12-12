$(document).ready(function(){
  var socket = io('/room', {transport: ['websocket']});

  socket.on('paint', function(gridData){

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
            if (d.hero1 > 0){
                return "blue";
            } else if (d.hero2 > 0) {
                return "red";
            }else{
                return "white";
            }
        })
        .attr("stroke", "#222")
  });


  socket.on('start_game', function(data){
    $('#log_window').append('<li>The user '+data.player1+' is playing with class '+data.player1_class+'</li>');
    $('#log_window').append('<li>The user '+data.player2+' is playing with class '+data.player2_class+'</li>');
    $('#log_window').append('<li>The user '+ data.player_turn+' starts playing.</li>');
  });

  socket.on('message', function(data){
    $('#log_window').append('<br>'+data)
  });

  $('#up').click(function(){
    data = 'up';
    socket.emit('game_move', data);
  });
  $('#down').click(function(){
    data = 'down';
    socket.emit('game_move', data);
  });
  $('#left').click(function(){
    data = 'left';
    socket.emit('game_move', data);
  });
  $('#right').click(function(){
    data = 'right';
    socket.emit('game_move', data);
  });
  $('#attack').click(function(){
    socket.emit('game_attack');
  });

  socket.on('new_connection', function(data){
    $('#log_window').append('<li>'+data.connection+'</li>');
  });
  socket.on('new_disconnection', function(data){
    $('#log_window').append('<li>'+data.disconnection+'</li>');
  });
  socket.on('finish', function(data){
      alert(data.message);
  });
});
