var known;

function pageLoad()
{
	$.getJSON( "/api/known", function( data ) {
		known = data;
		var channels_array = Object.keys(data);
		var channels = $("#channel");
		
		channels_array.sort();
		
		channels_array.forEach( function(v, i, a) {
			channels.append($("<option />").val(v).text(v));
		});
	});
}

function channelChange()
{
	var users = $("#user");
	var channel = $('#channel').val();
	
	users.empty();
	users.append($("<option />"));
	
	if(channel == "")
	{
		return;
	}
	
	known[channel].sort();
	
	known[channel].forEach( function(v, i, a) {
		users.append($("<option />").val(v).text(v));
	});
}

function userChange()
{
	var result = $("#result");
	var user = $('#user').val();
	var channel = $('#channel').val();
	var limit = $('#limit').val();
	
	result.empty();
	
	if(user == "" || channel == "")
	{
		return;
	}
	
	$.getJSON( "/api/log/" + channel + "/" + user + "/?limit=" + limit , function( data ) {
		data.forEach( function(v, i, a) {
			var time = $("<p />").text(v.utc).toggleClass("timestamp");
			var chat = $("<p />").text(v.chat).toggleClass("message");
			var line = $("<div />").toggleClass("chatline");
			line.append(time);
			line.append(chat);
			result.append(line);
		});
	});
}