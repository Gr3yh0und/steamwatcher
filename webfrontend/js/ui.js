var userid = 0;
document.getElementById('user_name').innerHTML = "<h3>Please select a user first!</h3>";

// load user menu
var result = jQuery.parseJSON($.ajax({
	url: baseurl + "/user/list/",
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