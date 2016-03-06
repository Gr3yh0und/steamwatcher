google.charts.load('current', {
    packages: ['corechart', 'bar', 'calendar']
});
google.charts.setOnLoadCallback(drawMonthlyDetails);
google.charts.setOnLoadCallback(drawAppDistribution);
google.charts.setOnLoadCallback(drawYearlyPlaytime);
google.charts.setOnLoadCallback(drawCalendar);

function drawMonthlyDetails() {

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
    var chart = new google.visualization.ColumnChart(document.getElementById('chart_monthly_details'));
    chart.draw(data, options);
}

function drawAppDistribution() {
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
    var chart = new google.visualization.PieChart(document.getElementById('chart_app_distribution'));
    chart.draw(data, options);
}

function drawYearlyPlaytime() {

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
        document.getElementById('chart_yearly_playtime'));

    chart.draw(data, options);
}


function drawCalendar() {
    var jsonData = $.ajax({
        url: "http://127.0.0.1:5000/block/month/last365/user/4/",
        dataType: "json",
        async: false
    }).responseText;

    var data = new google.visualization.DataTable(jsonData);
    var chart = new google.visualization.Calendar(document.getElementById('calendar_basic'));

    var options = {
        title: "Playtime calendar",
        height: 350,
    };

    chart.draw(data, options);
}

function drawWeeklyDetails() {

    var jsonData = $.ajax({
        url: "http://127.0.0.1:5000/block/week/last/user/4/",
        dataType: "json",
        async: false
    }).responseText;

    var options = {
        title: 'Playtime for last 7 days',
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
    var chart = new google.visualization.ColumnChart(document.getElementById('chart_weekly_playtime'));
    chart.draw(data, options);
}