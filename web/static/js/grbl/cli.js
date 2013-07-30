// Enable console debugging, when Josh.Debug is set and there is a console object on the document root.
var _console = (Josh.Debug && window.console) ? window.console : {
	log : function() {
	}
};
//
//Josh = {Debug: false };

// Create `History` and `KillRing` by hand since we will use the `KillRing` for
// an example command.
var history = Josh.History();
var killring = new Josh.KillRing();

// Create the `ReadLine` instance by hand so that we can provide it our
// `KillRing`. Since the shell needs to share
// the `History` object with `ReadLine` and `Shell` isn't getting to create
// `ReadLine` automatically as it usually does
// we need to pass in `History` into `ReadLine` as well.
var readline = new Josh.ReadLine({
	history : history,
	killring : killring,
	console : _console
});

// Finally, create the `Shell`.
var shell = Josh.Shell({
	readline : readline,
	history : history,
	console : _console,
	prompt : "$"
});

/* override default command handler */
shell.setCommandHandler("_default", {
	exec : function(cmd, args, callback) {
		var command = cmd;
		if (args.length > 0) {
			command += " "+args.join(" ");
		}
		callback();
		Grbl.send(command);
	},
	completion : function(cmd, arg, line, callback) {
		if (!arg) {
			arg = cmd;
		}
		return callback(shell.bestMatch(arg, shell.commands()));
	}
});

/* add custom enable/disable methods to the shell */
shell.disable = function() {
	shell.deactivate();
	$("#shell-cli").css("opacity", 0.1);
};

shell.enable = function() {
	shell.activate();
	$("#shell-cli").css("opacity", 1);
};

// Setup Document Behavior
// -----------------------

// Activation and display behavior happens at document ready time.
$(document).ready(function() {

	shell.enable();

});
