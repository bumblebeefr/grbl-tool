function resize() {
	$("#shell-panel").height(window.innerHeight - 105);
	$("body").height(window.innerHeight);
};
$(window).resize(resize);

$(function() {
	resize();
	$(".btn-auto-connect").click(function() {
		Grbl.send("connect");
	});
	$("#bbtn-manual-connect").click(function(){
		var bitrate = parseInt($("#connection-bitrate").val());
		if(isNaN(bitrate)){
			alert('Bitrate must be a valid value');
		}else{
			Grbl.send("connect "+$("#connection-device").val()+" "+bitrate);
		}
	});
	$("#connection-bitrate,#connection-device").click(function(e){
		e.stopPropagation();
	});
	$(".btn-disconnect").click(function() {
		Grbl.send("disconnect");
	});

	$.each([ 'x', 'y', 'z' ], function(k, axis) {
		$.each({
			"01" : 0.1,
			"1" : 1,
			"10" : 10,
			"100" : 100
		}, function(j, value) {
			$("#bt_" + axis + "_p" + j).click(function() {
				Grbl.send("G01 " + axis + value);
			});
			$("#bt_" + axis + "_m" + j).click(function() {
				Grbl.send("G01 " + axis + "-" + value);
			});
		});
	});
});
