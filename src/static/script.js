var known;

function pageLoad()
{
	$("#user").autocomplete({
		select: function(e,i){setTimeout(userChange,100);}
	});
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

	if(channel == "")
	{
		users.autocomplete("destroy");
		return;
	}

	users.autocomplete({
		source: known[channel]
	});
	users.autocomplete("enable");

	/*users.empty();
	users.append($("<option />"));

	known[channel].sort();

	known[channel].forEach( function(v, i, a) {
		users.append($("<option />").val(v).text(v));
	});*/
}

function userChange()
{
	var result = $("#result");
	var user = $('#user').val();
	var channel = $('#channel').val();
	var limit = $('#limit').val();

	console.log(user);

	result.empty();

	if(user == "" || channel == "")
	{
		return;
	}
	if(known[channel].indexOf(user) != -1)
	{
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
}
