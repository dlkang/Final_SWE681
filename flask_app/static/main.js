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
	.style("fill", "#fff")
	.style("stroke", "#222")
	.on('click', function(d) {
	        console.log("Click!");
	        d3.select(this).style("background-color", "#f9886c")})