var baseurl = 'http://127.0.0.1:5000';
var userid = 6;

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
				drawLastWeek();
			}
		);
        break;
		
    case 'last_month':
		document.getElementById('title').innerHTML = 'Last Month';
        google.charts.setOnLoadCallback(
			function () {
				drawLastMonth();
			}
		);
        break;
		
	case 'last_year':
		document.getElementById('title').innerHTML = 'Last Year';
        google.charts.setOnLoadCallback(drawLastYear);
        break;
	
	case 'for_days':
		document.getElementById('dropdown_days').style.display = 'inline';
		document.getElementById('title').innerHTML = 'For ' + i + ' Days';
        google.charts.setOnLoadCallback(
			function () {
				drawLastDays(i);
			}
		);
        break;
	} 
}


function drawLastDays(days) {
	$.ajax({
        url: baseurl + "/block/last/days/" + days + "/user/" + userid + "/",
        dataType: "json",
        async: true
    }).done(function(result){

		var options = {
			title: 'Playtime for last ' + days + ' days',
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
	});
}

function drawLastWeek(){
	drawLastDays(7);
}

function drawLastMonth(){
	drawLastDays(30);
}

function drawLastYear() {
    $.ajax({
        url: baseurl + "/block/month/last12/user/" + userid + "/",
        dataType: "json",
        async: true
    }).done(function(result){

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
	});
}


function drawGivenMonth() {
    $.ajax({
        url: baseurl + "/block/month/details/" + month + "/user/" + userid + "/",
        dataType: "json",
        async: true
    }).done(function(result){
		
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
	});   
}



function drawAppDistribution() {
    $.ajax({
        url: baseurl +"/block/month/playtime/" + month + "/user/" + userid + "/",
        dataType: "json",
        async: true
    }).done(function(result){

		var options = {
			title: 'Games in month ' + month,
			pieHole: 0.4,
			height: 450,
		};

		var data = new google.visualization.DataTable(result);
		var chart = new google.visualization.PieChart(document.getElementById('chart_app_distribution'));
		chart.draw(data, options);
		
	});
}



function drawCalendar() {
    $.ajax({
        url: baseurl + "/block/month/last365/user/" + userid + "/",
        dataType: "json",
        async: true
    }).done(function(result){

		var data = new google.visualization.DataTable(result);
		var chart = new google.visualization.Calendar(document.getElementById('calendar_basic'));

		var options = {
			title: "Playtime calendar",
			height: 350,
		};

		chart.draw(data, options);
	});
}

