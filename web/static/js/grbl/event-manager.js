var EventManager = {
	_findHandler : function(arr_property, obj) {
		var key = arr_property.shift();
		if ((arr_property.length == 0) && (typeof obj[key] == 'function')) {
			return obj[key];
		}
		if ((arr_property.length > 0) && (typeof obj[key] == 'object')) {
			return EventManager._findHandler(arr_property, obj[key]);
		} else {
			return function() {
			};
		}
	},
	_handleEvent : function(event, data) {
		try {
			EventManager._findHandler(event.split("."), EventManager)(data);
		} catch (e) {
			console.error("Error processing event ", event, data, e);
		}
	},
	console : {
		info : function(data) {
			shell.log("info", data.message);
		},
		debug : function(data) {
			shell.log("debug", data.message);
		},
		warn : function(data) {
			shell.log("warn", data.message);
		}
	},
	serial : {
		connected : function(data) {
			$("#serial-connected").text(data.port+"@"+data.bitrate);
			$("#menu-connect").hide();
			$("#menu-disconnect").show();
		},
		disconnected : function(data) {
			$("#serial-connected").text("Disconnected");
			$("#menu-connect").show();
			$("#menu-disconnect").hide();
		},
	},
	status : function(data) {
		$("#status-state").text(data.status);
		$("#machine-x").text(numeral(data['machine.x']).format("0.000"));
		$("#machine-y").text(numeral(data['machine.y']).format("0.000"));
		$("#machine-z").text(numeral(data['machine.z']).format("0.000"));
		$("#work-x").text(numeral(data['work.x']).format("0.000"));
		$("#work-y").text(numeral(data['work.y']).format("0.000"));
		$("#work-z").text(numeral(data['work.z']).format("0.000"));
	},
	grbl : {
		input : function(data) {
			shell.log("grbl-input", data.message);
		},
		output : function(data) {
			shell.log("grbl-output", data.message);
		},
	}
};