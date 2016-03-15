var userid = 0;

// load user menu
var result = jQuery.parseJSON($.ajax({
	url: "http://127.0.0.1:5000/user/list/",
	dataType: "json",
	async: false
}).responseText);
for (i = 0; i < result.length; i++) {
	$('#user_dropdown').append('<li><a onClick="changeUser('+ result[i].id +', \''+ result[i].name +'\');">' + result[i].name + '</a></li>');
}

// change user id and name
function changeUser(newid, name){
	userid = newid;
	document.getElementById('user_name').innerHTML = "<h3>User Details for " + name + "</h3>";
}