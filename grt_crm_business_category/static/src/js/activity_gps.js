odoo.define("grt_crm_business_category.activity_gps_simple", function (require) {
    "use strict";

    var core = require("web.core");
    var Dialog = require("web.Dialog");
    var FormController = require("web.FormController");
    var ajax = require("web.ajax");

    var _t = core._t;
    var pendingGpsCoords = null;

    // GPS Configuration
    var GPS_TIMEOUT = 8000;
    var GPS_BACKGROUND_INTERVAL = 60000;

    // Simple promise-based getCurrentPosition
    function getCurrentPosition() {
        return new Promise(function(resolve, reject) {
            if (!navigator.geolocation) {
                return reject("Geolocation not available");
            }

            navigator.geolocation.getCurrentPosition(
                function (position) {
                    var coords = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy
                    };
                    console.log("[GPS] Captured high accuracy:", coords);
                    pendingGpsCoords = coords;
                    resolve(coords);
                },
                function (error) {
                    console.warn("[GPS] High accuracy failed, trying low accuracy:", error.message);
                    // Try low accuracy fallback
                    navigator.geolocation.getCurrentPosition(
                        function (position) {
                            var coords = {
                                latitude: position.coords.latitude,
                                longitude: position.coords.longitude,
                                accuracy: position.coords.accuracy
                            };
                            console.log("[GPS] Captured low accuracy:", coords);
                            pendingGpsCoords = coords;
                            resolve(coords);
                        },
                        function (err) {
                            console.error("[GPS] Both attempts failed:", err.message);
                            reject(err.message);
                        },
                        {enableHighAccuracy: false, timeout: 10000, maximumAge: 60000}
                    );
                },
                {enableHighAccuracy: true, timeout: GPS_TIMEOUT, maximumAge: 0}
            );
        });
    }

    // Background GPS capture every 60 seconds
    function captureGpsInBackground() {
        getCurrentPosition()
            .then(function (coords) {
                console.log("[GPS] Background capture successful");
                
                // Send to server
                var now = new Date();
                var localTime = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-' + String(now.getDate()).padStart(2, '0') + ' ' + String(now.getHours()).padStart(2, '0') + ':' + String(now.getMinutes()).padStart(2, '0') + ':' + String(now.getSeconds()).padStart(2, '0');
                ajax.jsonRpc("/grt_crm_business_category/gps/ping", "call", {
                    latitude: coords.latitude,
                    longitude: coords.longitude,
                    client_time: localTime,
                    client_tz: Intl.DateTimeFormat().resolvedOptions().timeZone || ""
                }).catch(function (err) {
                    console.warn("[GPS] Background ping failed:", err);
                });
            })
            .catch(function (err) {
                console.warn("[GPS] Background capture failed:", err);
            });
    }

    // Start background capture
    console.log("[GPS] Initializing background GPS capture");
    setTimeout(captureGpsInBackground, 2000);
    setInterval(captureGpsInBackground, GPS_BACKGROUND_INTERVAL);

    // Extend FormController for activity forms
    FormController.include({
        
        _update: function () {
            var result = this._super.apply(this, arguments);
            var self = this;
            
            // Attach GPS button handler when form loads
            if (this.modelName === 'mail.activity') {
                result.then(function() {
                    self._attachGpsButtonHandler();
                });
            }
            
            return result;
        },
        
        _attachGpsButtonHandler: function() {
            var self = this;
            console.log("[GPS] Looking for button...");
            
            // Multiple selector attempts
            var $button = this.$('[name="gps_capture_btn"]');
            if ($button.length === 0) {
                $button = this.$('.grt_capture_gps_btn');
            }
            if ($button.length === 0) {
                $button = this.$('.o_activity_gps_btn');
            }
            
            if ($button.length > 0) {
                console.log("[GPS] Button found, attaching click handler");
                $button.off('click').on('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    self._captureGpsAndUpdate();
                    return false;
                });
            } else {
                console.warn("[GPS] Button not found in DOM");
            }
        },
        
        _captureGpsAndUpdate: function() {
            var self = this;
            console.log("[GPS] Manual capture started");
            
            getCurrentPosition()
                .then(function(coords) {
                    console.log("[GPS] Manual capture successful:", coords);
                    
                    // Show success notification
                    var msg = "GPS berhasil di-capture: " + coords.latitude.toFixed(6) + ", " + coords.longitude.toFixed(6);
                    Dialog.alert(self, msg, { title: 'GPS Captured' });
                    
                    // Update the form fields using the correct Odoo 14 approach
                    self._updateActivityGpsFieldsOdoo14(coords);
                })
                .catch(function(err) {
                    console.error("[GPS] Manual capture failed:", err);
                    Dialog.alert(self, "Gagal: " + err, { title: 'GPS Error' });
                });
        },
        
        _updateActivityGpsFieldsOdoo14: function(coords) {
            console.log("[GPS] Updating activity fields (Odoo 14 proper method)");
            
            var self = this;
            var handle = this.handle;
            var model = this.model;
            
            try {
                // Get the current record
                var record = model.get(handle);
                console.log("[GPS] Current record:", record);
                
                if (!record) {
                    console.error("[GPS] Record not found");
                    return;
                }
                
                // Direct record data update (Odoo 14 way)
                var osmUrl = "https://www.openstreetmap.org/?mlat=" + coords.latitude + "&mlon=" + coords.longitude + "#map=18/" + coords.latitude + "/" + coords.longitude;
                var now = new Date();
                var localTime = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-' + String(now.getDate()).padStart(2, '0') + ' ' + String(now.getHours()).padStart(2, '0') + ':' + String(now.getMinutes()).padStart(2, '0') + ':' + String(now.getSeconds()).padStart(2, '0');
                var changes = {
                    gps_captured: true,
                    gps_latitude: coords.latitude,
                    gps_longitude: coords.longitude,
                    gps_openstreetmap_url: osmUrl,
                    gps_client_time: localTime,
                    gps_client_tz: Intl.DateTimeFormat().resolvedOptions().timeZone || ""
                };
                
                // Update internal record data
                _.extend(record.data, changes);
                console.log("[GPS] Record data updated:", record.data);
                
                // Method 1: Try notifyChanges with a changes object
                try {
                    model.notifyChanges(handle, changes);
                    console.log("[GPS] notifyChanges called with changes object");
                } catch (e) {
                    console.warn("[GPS] notifyChanges with changes failed:", e.message);
                }
                
                // Method 2: Try calling notifyChanges without params
                try {
                    model.notifyChanges(handle);
                    console.log("[GPS] notifyChanges called without params");
                } catch (e) {
                    console.warn("[GPS] notifyChanges simple failed:", e.message);
                }
                
                // Method 3: Force renderer update after delay
                setTimeout(function() {
                    try {
                        if (self.renderer && self.renderer.update) {
                            var state = model.get(handle, {raw: true});
                            self.renderer.update(state);
                            console.log("[GPS] Renderer.update called");
                        }
                    } catch (e) {
                        console.warn("[GPS] Renderer update failed:", e.message);
                    }
                }, 100);
                
                // Method 4: Update DOM inputs for display only (no change trigger)
                setTimeout(function() {
                    console.log("[GPS] Attempting direct DOM update...");
                    var $latInput = self.$('input[name="gps_latitude"]');
                    var $lonInput = self.$('input[name="gps_longitude"]');
                    
                    if ($latInput.length) {
                        $latInput.val(coords.latitude);
                        console.log("[GPS] DOM lat input display updated to", coords.latitude);
                    }
                    if ($lonInput.length) {
                        $lonInput.val(coords.longitude);
                        console.log("[GPS] DOM lon input display updated to", coords.longitude);
                    }

                    var $urlInput = self.$('input[name="gps_openstreetmap_url"]');
                    if ($urlInput.length) {
                        $urlInput.val(osmUrl);
                        console.log("[GPS] DOM URL input display updated");
                    }
                    
                    // Also check for the checkbox
                    var $capturedCheckbox = self.$('input[name="gps_captured"]');
                    if ($capturedCheckbox.length) {
                        $capturedCheckbox.prop('checked', true);
                        console.log("[GPS] gps_captured checkbox display checked");
                    }
                }, 150);
                
            } catch (err) {
                console.error("[GPS] Error updating fields:", err, err.stack);
            }
        }
    });

    console.log("[GPS] Module loaded successfully");
});

