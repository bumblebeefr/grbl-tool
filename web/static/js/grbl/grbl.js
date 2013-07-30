var Grbl = {
	send : function(command){
		shell.disable();
		$.ajax("/command.json", {
			data : {
				cmd : command
			},
			success : function(data) {
				console.debug(command, "ok", data);
				shell.enable();
			},
			error : function() {
				console.error(command, "ko");
				shell.enable();
			}
		});
	}
};