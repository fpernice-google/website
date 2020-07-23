// Page Setup.
// Configure map projection options, create map and value objects.
var projection = d3.geoMercator()
  .translate([450, 420])
  .scale(140);
var geomap = d3.geoPath().projection(projection);
var glob_values = null

// Get chart parameters from url request.
var url = new URL(window.location.href);
var statVar = url.searchParams.get("statVar");
var perCapita = url.searchParams.get("perCapita") == "true";

// Create HTTP request to server to get value data.
var xmlhttp = new XMLHttpRequest();
xmlhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var values = JSON.parse(this.responseText)[0];
      glob_values = values;
      d3.json('worldgeo.json', function(_, json) {
        generateGeoMap(json, values)
      })
    }
  };
base_url = "http://0.0.0.0/api/data?"
base_url += "statVar=" + statVar
base_url += "&perCapita=" + perCapita
xmlhttp.open("GET", base_url, true);
xmlhttp.send();

/**
 * Handles the creation of d3 map from geojson file.
 * @param {json} geojson entire geoJson map.
 */
function generateGeoMap(geojson, values) {
    // Combine path elements from D3 content.
    var mapContent = d3.select("#content g.map")
        .selectAll("path")
        .data(geojson.features);

    // Build chart display options.
    plt_info = values['_PLOTTING_INFO'];
    var colorScale = d3.scaleLinear()
            .domain([plt_info['lower_bound'], plt_info['upper_bound']])
            .range(["#77C7EF", "#2E9BD1", "#0C6794"]);

    // Build map objects.
    mapContent.enter()
        .append("path")
        .attr("d", geomap)
        // Add CSS class to each path for border outlining.
        .attr("class", "border")
        .attr("fill", function (d) {
            country_dcid = d.id
            if (country_dcid in values) {
                value = values[country_dcid]
                return colorScale(value)
            } else {
                return "gray";
            }
          })
        // Add various country level event handlers.
        .on("mouseover", handleMapHover)
        .on("mouseleave", mouseLeave)
        .on("click", handleMapClick);
}

/**
 * Capture hover event on country and displays relevant information.
 * @param {json} country is the geoJson content for the hovered country.
 */
function handleMapHover(country) {
  // Display statistical variable information on hover.
  let name = country.properties.name;
  let dcid = country.properties.dcid;
  if (dcid in glob_values) {
      document.getElementById("display").innerHTML =
          name + " - " + glob_values[dcid];
  } else {
      document.getElementById("display").innerHTML = name + " - No Value";
  }
  
  // Change dashed line to complete line to highlight country.
  d3.select(this).style("stroke-dasharray", 0);
}

/**
 * Clears output after leaving a country.
 */
function mouseLeave() {
  // Remove hover text.
  document.getElementById("display").innerHTML = "";

  // Set country border back to dashed line.
  d3.select(this).style("stroke-dasharray", 5);
}

/**
 * Capture click event on country and redirects user to that page in the browser.
 * @param {json} country is the geoJson content for the clicked country.
 */
function handleMapClick(country) {
    window.location.href = "https://datacommons.org/place?dcid=" + 
        country.properties.dcid;
}