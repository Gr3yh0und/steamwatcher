var baseurl = 'http://127.0.0.1:5000';
var userid = 4;

google.charts.load('current', {
    packages: ['corechart', 'bar', 'calendar']
});

// list of all possible options in the left navbar
var options = ["last_week", "last_month", "last_year", "for_days"];


// change the CSS class in the navbar according to the current selection (to .active-second)
function handleActive(option){
	for (i = 0; i < options.length; i++) {
		if(options[i] !== option){
			document.getElementById(options[i]).className = '';
		}else{
			document.getElementById(options[i]).className = 'active-second';
		}
	}	
}

// draw the diagram
function draw(diagram, i){
	handleActive(diagram);
	document.getElementById('dropdown_days').style.display = 'none';
	
	switch(diagram) {
    case 'last_week':
		document.getElementById('title').innerHTML = 'Last Week';
        google.charts.setOnLoadCallback(
			function () {
				document.getElementById('chart_calendar').innerHTML = "";
				drawLastDays(7);
			}
		);
        break;
		
    case 'last_month':
		document.getElementById('title').innerHTML = 'Last Month';
        google.charts.setOnLoadCallback(
			function () {
				document.getElementById('chart_calendar').innerHTML = "";
				drawLastDays(30);
			}
		);
        break;
		
	case 'last_year':
		document.getElementById('title').innerHTML = 'Last Year';
        google.charts.setOnLoadCallback(drawLastYear);
		google.charts.setOnLoadCallback(drawCalendar);
        break;
	
	case 'for_days':
		document.getElementById('dropdown_days').style.display = 'inline';
		document.getElementById('title').innerHTML = 'For the last ' + i + ' Days';
        google.charts.setOnLoadCallback(
			function () {
				document.getElementById('chart_calendar').innerHTML = "";
				drawLastDays(i);
			}
		);
        break;
	} 
}

function drawDays(result, title) {
	var options = {
		title: title,
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

	var data = new google.visualization.DataTable(result.details);
	var chart = new google.visualization.ColumnChart(document.getElementById('chart_main'));
	chart.draw(data, options);
}

function drawLastDays(days) {
	$.ajax({
		url: baseurl + "/block/last/days/" + days +"/user/" + userid + "/",
		dataType: "json",
		async: true
	})
	.done(function(result){
		drawDays(result, 'Playtime for last ' + days + ' days');
		drawAppDistribution(result, 'App distribution for the last ' + days + ' days');
		document.getElementById('statistics').innerHTML = "Total playtime: " + Math.round(result.statistics.total/60) + " hours";
	})
	.fail(function(result){
		error = jQuery.parseJSON(result.responseText);
		document.getElementById('chart_main').innerHTML = "<h3>" + error.errors[0].userMessage + "</h3>";
		document.getElementById('chart_distribution').innerHTML = "";
	});
}

function drawLastYear() {
	document.getElementById('chart_distribution').innerHTML = "";
    $.ajax({
        url: baseurl + "/block/month/last12/user/" + userid + "/",
        dataType: "json",
        async: true
    })
	.done(function(result){
		document.getElementById('statistics').innerHTML = "Total playtime: " + Math.round(result.total/60/24) + " days (" + Math.round(result.total/60) + " hours)";

		var options = {
			title: 'Playtime per Month in the last year',
			hAxis: {
				title: 'Month'
			},
			vAxis: {
				title: 'Playtime in Minutes'
			},
			legend: 'none'
		};

		var data = new google.visualization.DataTable(result);
		var chart = new google.visualization.ColumnChart(
			document.getElementById('chart_main'));

		chart.draw(data, options);
	})
	.fail(function(result){
		document.getElementById('statistics').innerHTML = "";
		error = jQuery.parseJSON(result.responseText);
		document.getElementById('chart_main').innerHTML = "<h3>" + error.errors[0].userMessage + "</h3>";
	});
}


function drawGivenMonth() {
    $.ajax({
        url: baseurl + "/block/month/details/" + month + "/user/" + userid + "/",
        dataType: "json",
        async: true
    })
	.done(function(result){
		
		var options = {
			title: 'Playtime for ' + month,
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

		var data = new google.visualization.DataTable(result);
		var chart = new google.visualization.ColumnChart(document.getElementById('chart_main'));
		chart.draw(data, options);
	})
	.fail(function(result){
		error = jQuery.parseJSON(result.responseText);
		document.getElementById('chart_main').innerHTML = "<h3>" + error.errors[0].userMessage + "</h3>";
	});   
}


function drawAppDistribution(result, title) {
	var options = {
		title: title,
		pieHole: 0.4,
		height: 450,
	};

	console.log(result);
	var data = new google.visualization.DataTable(result.distribution);
	var chart = new google.visualization.PieChart(document.getElementById('chart_distribution'));
	chart.draw(data, options);
}


function drawCalendar() {
    $.ajax({
        url: baseurl + "/block/month/last365/user/" + userid + "/",
        dataType: "json",
        async: true
    })
	.done(function(result){

		var data = new google.visualization.DataTable(result);
		var chart = new google.visualization.Calendar(document.getElementById('chart_calendar'));

		var options = {
			title: "Playtime calendar",
			height: 350,
		};

		chart.draw(data, options);
	})
	.fail(function(result){
		error = jQuery.parseJSON(result.responseText);
		document.getElementById('chart_calendar').innerHTML = "<h3>" + error.errors[0].userMessage + "</h3>";
	});
}

