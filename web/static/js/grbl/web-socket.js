/**
 * Gestion des websockets : ouverture et reouverture automatique de websocket,
 * gestion des messages, ...
 */
var WS = {
    active : false,
    open : function() {
        if ("WebSocket" in window) {
            try {
                WS.ws = new WebSocket("ws://" + document.domain
                        + (document.location.port == "" ? "":":"+document.location.port)+"/websocket");
                WS.ws.onmessage = function(msg) {
                    var message = JSON.parse(msg.data);
                    if(console){
                        console.debug(message);
                    }
                    if(message.type){
                    	EventManager._handleEvent(message.type,message.data);
                    }
                    
                    WS.set_active(true);
                };
                WS.ws.onclose = function() {
                    WS.set_active(false);
                };
            } catch (err) {
                console.error("Unable to connect to the web socket", err);
                WS.set_active(false);
            }
        }
    },
    set_active : function(active) {
        WS.active = active;
// $("body").css("opacity",(active ? 1: 0.1));
        if (!active) {
        	alert("Web socket is closed");
        	window.close();
            setTimeout(WS.open, 5000);
        }
    }
};

window.onbeforeunload = function() {
    WS.ws.close()
};

WS.open();
