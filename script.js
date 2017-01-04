var margin = {top: 20, right: 20, bottom: 30, left: 40},
    w = 800 - margin.right - margin.left,
    h = 600 - margin.top - margin.bottom,
    data_url = "d3data.csv";

var x = d3.scale.linear().range([0, w]),
    y = d3.scale.linear().range([h, 0]);

var xAxis = d3.svg.axis().scale(x).orient("bottom"),
    yAxis = d3.svg.axis().scale(y).orient("left");              


var svg = d3.select("#medalChart")
            .append("svg")
            .attr("width", w + margin.left + margin.right)
            .attr("height", h + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var tooltip = d3.select("#medalChart").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

var getGdp = function(d) {
      //gdp = 
      return '$' + Math.round(d._2015_gdp_per_capita).toLocaleString(); 
    };

var getMedals = function(d) { return d.total; };


d3.csv(data_url, function(data) {

  data.forEach(function(d) {
    d.country = d.country;
    d.gold = +d.gold;
    d.silver = +d.silver;
    d.bronze = +d.bronze;
    d.total = +d.total;
    d.country_code = d.country_code;
    d._2015_gdp_per_capita = +d._2015_gdp_per_capita;

    console.log(d)
  });

  x.domain(d3.extent(data, function(d) { return d._2015_gdp_per_capita; })).nice();
  y.domain(d3.extent(data, function(d) { return d.total; })).nice();
  
  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + h + ")")
      .call(xAxis)
      .append("text")
      .attr("class", "label")
      .attr("x", w)
      .attr("y", -6)
      .style("text-anchor", "end")
      .text("GDP Per Capita (2015, USD)");

svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
      .append("text")
      .attr("class", "label")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("2015 Summer Olympic Medals")

svg.selectAll(".dot")
      .data(data)
      .enter().append("circle")
      .attr("class", "dot")
      .attr("r", 3.5)
      .attr("cx", function(d) { return x(d._2015_gdp_per_capita); })
      .attr("cy", function(d) { return y(d.total); })
      .style("fill", "red")
      .on("mouseover", function(d) {
          tooltip.transition()
               .duration(200)
               .style("opacity", .9);
          tooltip.html(d.country + "<br/> (" + getGdp(d)
          + ", " + getMedals(d) + ")")
               .style("left", (d3.event.pageX + 5) + "px")
               .style("top", (d3.event.pageY - 28) + "px");
      })
      .on("mouseout", function(d) {
          tooltip.transition()
               .duration(500)
               .style("opacity", 0);
      });

});
