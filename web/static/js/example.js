/*------------------------------------------------------------------------*
 * Copyright 2013 Arne F. Claassen
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *-------------------------------------------------------------------------*/
(function(root, $, _) {
  Josh.Example = (function(root, $, _) {

    // Enable console debugging, when Josh.Debug is set and there is a console object on the document root.
    var _console = (Josh.Debug && root.console) ? root.console : {
      log: function() {
      }
    };

    // Create `History` and `KillRing` by hand since we will use the `KillRing` for an example command.
    var history = Josh.History();
    var killring = new Josh.KillRing();

    // Create the `ReadLine` instance by hand so that we can provide it our `KillRing`. Since the shell needs to share
    // the `History` object with `ReadLine` and `Shell` isn't getting to create `ReadLine` automatically as it usually does
    // we need to pass in `History` into `ReadLine` as well.
    var readline = new Josh.ReadLine({history: history, killring: killring, console: _console });

    // Finally, create the `Shell`.
    var shell = Josh.Shell({readline: readline, history: history, console: _console,prompt:"$"});


    // Create *killring* command
    // -------------------------

    // Setup the `Underscore` template for displaying items in the `KillRing`.
    var killringItemTemplate = _.template("<div><% _.each(items, function(item, i) { %><div><%- i %>&nbsp;<%- item %></div><% }); %></div>")

    // Create a the command `killring` which will display all text currently in the `KillRing`, by attaching
    // a handler to the `Shell`.
    shell.setCommandHandler("killring", {

      // We don't implement any completion for the `killring` command, so we only provide an `exec` handler, and no `completion` handler.
      exec: function(cmd, args, callback) {

        // `killring` takes one optional argument **-c** which clears the killring (just like **history -c**).
        if(args[0] == "-c") {
          killring.clear();

          // The callback of an `exec` handler expects the html to display as result of executing the command. Clearing the
          // killing has no output, so we just call the callback and exit the handler.
          callback();
          return;
        }

        // Return the output of feeding all items from the killring into our template.
        callback(killringItemTemplate({items: killring.items()}));
      }
    });

    
    // Setup Document Behavior
    // -----------------------

    // Activation and display behavior happens at document ready time.
    $(document).ready(function() {

      // The default name for the div the shell uses as its container is `shell-panel`, although that can be changed via
      // the shell config parameter `shell-panel-id`. The `Shell` display model relies on a 'panel' to contain a 'view'.
      // The 'panel' acts as the view-port, i.e. the visible portion of the shell content, while the 'view' is appended
      // to and scrolled up as new content is added.
      var $consolePanel = $('#shell-panel');
      shell.activate();
      shell.prompt("<div>coucou</div>",function(){});
			console.log(shell);
			
			$("a").click(function(){
      	shell.prompt("<div>coucou</div>",function(){});
			});
      
    });

    
  })(root, $, _);
})(this, $, _);
