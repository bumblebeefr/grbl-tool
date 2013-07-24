var EventManager  = {
    _findHandler : function(arr_property,obj){
        var key = arr_property.shift();
        if((arr_property.length == 0) && (typeof obj[key] == 'function')){
            return obj[key];
        }
        if((arr_property.length > 0) && (typeof obj[key] == 'object')){
            return EventManager._findHandler(arr_property,obj[key]);
        }else{
            return function(){};
        }
    },
    _handleEvent : function(event,data){
        try{
            EventManager._findHandler(event.split("."),EventManager)(data);
        }catch(e){
                  console.error("Error processing event ",event,data,e);
        }
    },
    console : {
        info : function(data){
        	shell.log("info",data.message);
        },
        debug : function(data){
        	shell.log("debug",data.message);
        },
        warn : function(data){
        	shell.log("warn",data.message);
        }
    }

}