google.charts.load('current', {
  packages: ['corechart', 'bar']
});
google.charts.setOnLoadCallback(drawStacked);
google.charts.setOnLoadCallback(drawChartDonut);
google.charts.setOnLoadCallback(drawBasic);

function drawStacked() {

  var jsonData = $.ajax({
    url: "http://127.0.0.1:5000/block/month/details/2016-02/user/4/",
    dataType: "json",
    async: false
  }).responseText;

  var options = {
    title: 'Playtime for 2016-02',
    isStacked: true,
    width: 1200,
    height: 450,
    hAxis: {
      title: 'Day'
    },
    vAxis: {
      title: 'Playtime in Minutes'
    }
  };

  var data = new google.visualization.DataTable(jsonData);
  var chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
  chart.draw(data, options);
}

function drawChartDonut() {
        var jsonData = $.ajax({
		url: "http://127.0.0.1:5000/block/month/playtime/2016-02/user/4/",
		dataType: "json",
		async: false
	  }).responseText;

        var options = {
          title: 'Games',
          pieHole: 0.4,
		  height: 450,
        };

		var data = new google.visualization.DataTable(jsonData);
        var chart = new google.visualization.PieChart(document.getElementById('donutchart'));
        chart.draw(data, options);
      }

function drawBasic() {

      var jsonData = $.ajax({
		url: "http://127.0.0.1:5000/block/month/last12/user/4/",
		dataType: "json",
		async: false
	  }).responseText;

      var options = {
        title: 'Playtime per Month in the year 2016',
        hAxis: {
          title: 'Month'
        },
        vAxis: {
          title: 'Playtime in Minutes'
        }
      };

	  var data = new google.visualization.DataTable(jsonData);
      var chart = new google.visualization.ColumnChart(
        document.getElementById('year'));

      chart.draw(data, options);
    }

