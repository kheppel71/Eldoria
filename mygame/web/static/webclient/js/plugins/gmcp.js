/*
 * Evennia Webclient GMCP Plugin
 *
 * Gracefully receives and processes GMCP (Generic MUD Communication Protocol) messages,
 * ensuring no "Error or Unhandled event" output is displayed in the webclient window.
 * Dispatches standard JavaScript CustomEvents ('evennia:gmcp' and 'evennia:gmcp:Room.Info')
 * so that any custom frontend widgets, mini-maps, or UI gauges can react in real-time.
 */

let gmcp_plugin = (function () {
    "use strict";

    var onGmcp = function (args, kwargs) {
        if (!args || args.length === 0) return true;
        var subpkg = args[0];
        var payload = kwargs || {};

        try {
            window.dispatchEvent(new CustomEvent("evennia:gmcp", {
                detail: { subpackage: subpkg, data: payload }
            }));

            if (subpkg === "Room.Info") {
                window.dispatchEvent(new CustomEvent("evennia:gmcp:Room.Info", {
                    detail: payload
                }));
            }
        } catch (e) {
            console.warn("[GMCP Plugin] Event dispatch warning:", e);
        }

        return true;
    };

    var onUnknownCmd = function (cmdname, args, kwargs) {
        if (cmdname === "gmcp" || cmdname === "GMCP") {
            return onGmcp(args, kwargs);
        }
        return false;
    };

    var init = function () {
        console.log("Evennia Webclient GMCP Plugin Initialized.");
    };

    return {
        init: init,
        onGmcp: onGmcp,
        onUnknownCmd: onUnknownCmd
    };
})();

if (typeof plugin_handler !== "undefined") {
    plugin_handler.add("gmcp", gmcp_plugin);
}

