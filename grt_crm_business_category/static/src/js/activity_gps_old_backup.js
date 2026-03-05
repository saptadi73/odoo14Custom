odoo.define("grt_crm_business_category.activity_gps", function (require) {
    "use strict";

    var core = require("web.core");
    var Dialog = require("web.Dialog");
    var rpc = require("web.rpc");
    var ajax = require("web.ajax");

    var _t = core._t;
    var originalQuery = rpc.query ? rpc.query.bind(rpc) : null;
    var mapClickHandlerRegistered = false;
    
    if (!originalQuery) {
        console.error("GRT GPS: rpc.query not available, GPS tracking disabled");
        return;
    }

    function showGpsWarning(message) {
        Dialog.alert(
            null,
            message ||
                _t(
                    "GPS belum aktif atau belum terdeteksi. Aktifkan izin lokasi di browser, lalu refresh halaman sebelum mengisi activity."
                )
        );
    }

    function getCurrentPosition() {
        var deferred = $.Deferred();
        
        console.log("GRT GPS: getCurrentPosition called");
        console.log("GRT GPS: navigator.geolocation available:", !!navigator.geolocation);
        console.log("GRT GPS: window.isSecureContext:", window.isSecureContext);
        console.log("GRT GPS: Current protocol:", window.location.protocol);
        console.log("GRT GPS: Current host:", window.location.host);
        
        if (!navigator.geolocation) {
            var msg = _t("Browser tidak mendukung Geolocation API.");
            console.error("GRT GPS:", msg);
            deferred.reject(msg);
            return deferred.promise();
        }
        
        // Try high accuracy first; fallback to lower accuracy for laptops/desktops.
        console.log("GRT GPS: Requesting position with high accuracy...");
        navigator.geolocation.getCurrentPosition(
            function (position) {
                console.log("GRT GPS: High accuracy success:", position.coords);
                deferred.resolve(position.coords);
            },
            function (errorHigh) {
                console.warn("GRT GPS: High accuracy failed, error code:", errorHigh.code, "message:", errorHigh.message);
                console.log("GRT GPS: Trying low accuracy fallback...");
                
                navigator.geolocation.getCurrentPosition(
                    function (position) {
                        console.log("GRT GPS: Low accuracy success:", position.coords);
                        deferred.resolve(position.coords);
                    },
                    function (error) {
                        var reason = _t("Lokasi tidak dapat diambil.");
                        if (error && error.code === 1) {
                            reason = _t("Izin lokasi ditolak oleh browser.");
                            console.error("GRT GPS: Permission denied (code 1)");
                        } else if (error && error.code === 2) {
                            reason = _t("Posisi tidak tersedia (sinyal/Wi-Fi lemah).");
                            console.error("GRT GPS: Position unavailable (code 2)");
                        } else if (error && error.code === 3) {
                            reason = _t("Permintaan lokasi timeout.");
                            console.error("GRT GPS: Timeout (code 3)");
                        }
                        if (!window.isSecureContext) {
                            reason +=
                                " " +
                                _t(
                                    "Koneksi saat ini bukan secure context. Buka Odoo via HTTPS atau http://localhost agar geolocation diizinkan browser."
                                );
                            console.error("GRT GPS: Not a secure context -", window.location.href);
                        }
                        console.error("GRT GPS: Both attempts failed. Final reason:", reason);
                        deferred.reject(reason);
                    },
                    {
                        enableHighAccuracy: false,
                        timeout: 25000,
                        maximumAge: 300000,
                    }
                );
            },
            {
                enableHighAccuracy: true,
                timeout: 12000,
                maximumAge: 0,
            }
        );
        return deferred.promise();
    }

    function pushGpsToServer(coords) {
        if (!coords) {
            return;
        }
        ajax.jsonRpc("/grt_crm_business_category/gps/ping", "call", {
            latitude: coords.latitude,
            longitude: coords.longitude,
            client_time: new Date().toLocaleString(),
            client_tz: Intl.DateTimeFormat().resolvedOptions().timeZone || "",
        }).fail(function (err) {
            console.warn("GRT GPS: Failed to push GPS ping to server", err);
        });
    }

    function normalizeCreateArgs(args) {
        if (!args || !args.length) {
            return null;
        }
        var firstArg = args[0];
        if (Array.isArray(firstArg)) {
            return {valuesList: firstArg, isList: true};
        }
        if (firstArg && typeof firstArg === "object") {
            return {valuesList: [firstArg], isList: false};
        }
        return null;
    }

    function isCrmCreateContext(params, valuesList) {
        var context = (params && params.kwargs && params.kwargs.context) || {};
        if (context.default_res_model === "crm.lead" || context.active_model === "crm.lead") {
            return true;
        }
        return valuesList.some(function (values) {
            return values && values.res_model === "crm.lead";
        });
    }

    function injectCoordinates(valuesList, coords, isCrmContext) {
        console.log("GRT GPS: injectCoordinates called with coords:", coords);
        console.log("GRT GPS: injectCoordinates valuesList before:", JSON.stringify(valuesList));
        
        var result = valuesList.map(function (values) {
            var updated = Object.assign({}, values);
            updated.gps_captured = true;
            updated.gps_latitude = coords.latitude;
            updated.gps_longitude = coords.longitude;
            updated.gps_client_time = new Date().toLocaleString();
            updated.gps_client_tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
            
            console.log("GRT GPS: Injected GPS fields - lat:", updated.gps_latitude, "lon:", updated.gps_longitude);
            
            if (isCrmContext) {
                var gpsUrl = buildGpsUrl(coords.latitude, coords.longitude);
                var gpsNoteHtml =
                    "<p>Update at GPS location: " +
                    coords.latitude +
                    ", " +
                    coords.longitude +
                    ' - <a href="' +
                    gpsUrl +
                    '" class="grt-gps-map-link" target="_blank">Open Maps</a></p>';
                updated.note = (updated.note || "") + gpsNoteHtml;
            }
            return updated;
        });
        
        console.log("GRT GPS: injectCoordinates result:", JSON.stringify(result));
        return result;
    }

    function getActivityIds(params) {
        if (!params || !params.args || !params.args.length) {
            return [];
        }
        var ids = params.args[0];
        return Array.isArray(ids) ? ids : [];
    }

    function injectGpsContext(params, coords) {
        var gpsUrl = buildGpsUrl(coords.latitude, coords.longitude);
        var kwargs = Object.assign({}, params.kwargs || {});
        var context = Object.assign({}, kwargs.context || {});
        context.gps_captured = true;
        context.gps_latitude = coords.latitude;
        context.gps_longitude = coords.longitude;
        context.gps_openstreetmap_url = gpsUrl;
        context.gps_done_client_time = new Date().toLocaleString();
        context.gps_done_client_tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
        kwargs.context = context;
        return Object.assign({}, params, {kwargs: kwargs});
    }

    function injectCreateGpsContext(params, coords) {
        var kwargs = Object.assign({}, params.kwargs || {});
        var context = Object.assign({}, kwargs.context || {});
        context.gps_captured = true;
        context.gps_latitude = coords.latitude;
        context.gps_longitude = coords.longitude;
        context.gps_client_time = new Date().toLocaleString();
        context.gps_client_tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
        kwargs.context = context;
        return Object.assign({}, params, {kwargs: kwargs});
    }

    function buildGpsUrl(latitude, longitude) {
        return (
            "https://www.openstreetmap.org/?mlat=" +
            latitude +
            "&mlon=" +
            longitude +
            "#map=18/" +
            latitude +
            "/" +
            longitude
        );
    }

    function registerMapModalHandler() {
        if (mapClickHandlerRegistered) {
            return;
        }
        mapClickHandlerRegistered = true;
        $(document).on("click", "a.grt-gps-map-link", function (ev) {
            var url = $(this).attr("href");
            if (!url || url.indexOf("openstreetmap.org") === -1) {
                return;
            }
            ev.preventDefault();
            openMapModal(url);
        });
    }

    function openMapModal(url) {
        var embedUrl = buildOsmEmbedUrl(url);
        var $content = $(
            '<div style="height:70vh;">' +
                '<iframe src="' +
                _.escape(embedUrl) +
                '" style="width:100%;height:100%;border:0;" allowfullscreen="allowfullscreen"></iframe>' +
            "</div>"
        );
        var dialog = new Dialog(null, {
            title: _t("GPS Location"),
            $content: $content,
            size: "large",
            buttons: [
                {
                    text: _t("Open in New Tab"),
                    classes: "btn-primary",
                    close: false,
                    click: function () {
                        window.open(url, "_blank");
                    },
                },
                {
                    text: _t("Close"),
                    close: true,
                },
            ],
        });
        dialog.open();
    }

    function buildOsmEmbedUrl(url) {
        try {
            var parsed = new URL(url, window.location.origin);
            var lat = parseFloat(parsed.searchParams.get("mlat"));
            var lon = parseFloat(parsed.searchParams.get("mlon"));
            if ((!isFinite(lat) || !isFinite(lon)) && parsed.hash && parsed.hash.indexOf("#map=") === 0) {
                var mapParts = parsed.hash.replace("#map=", "").split("/");
                if (mapParts.length >= 3) {
                    lat = parseFloat(mapParts[1]);
                    lon = parseFloat(mapParts[2]);
                }
            }
            if (!isFinite(lat) || !isFinite(lon)) {
                return "about:blank";
            }
            var delta = 0.01;
            var left = lon - delta;
            var right = lon + delta;
            var top = lat + delta;
            var bottom = lat - delta;
            return (
                "https://www.openstreetmap.org/export/embed.html?bbox=" +
                left +
                "%2C" +
                bottom +
                "%2C" +
                right +
                "%2C" +
                top +
                "&layer=mapnik&marker=" +
                lat +
                "%2C" +
                lon
            );
        } catch (err) {
            return "about:blank";
        }
    }

    registerMapModalHandler();

    // Add GPS status indicator to UI
    function addGpsStatusIndicator() {
        if ($('#grt_gps_status_indicator').length) {
            return; // Already added
        }
        
        var $indicator = $('<div id="grt_gps_status_indicator" style="' +
            'position: fixed; ' +
            'bottom: 10px; ' +
            'right: 10px; ' +
            'background: rgba(0,0,0,0.7); ' +
            'color: white; ' +
            'padding: 8px 12px; ' +
            'border-radius: 4px; ' +
            'font-size: 12px; ' +
            'z-index: 9999; ' +
            'cursor: pointer; ' +
            'box-shadow: 0 2px 8px rgba(0,0,0,0.3);' +
            '">' +
            '<span class="fa fa-map-marker"></span> GPS: <span id="grt_gps_status_text">Initializing...</span>' +
            '</div>');
        
        $indicator.on('click', function() {
            var msg = "GPS Status: " + gpsStatus + "\n" +
                      "Has coordinates: " + (!!pendingGpsCoords) + "\n" +
                      "Secure context: " + window.isSecureContext + "\n" +
                      "Protocol: " + window.location.protocol + "\n" +
                      "Host: " + window.location.host;
            
            if (pendingGpsCoords) {
                msg += "\n\nLatitude: " + pendingGpsCoords.latitude.toFixed(6) +
                       "\nLongitude: " + pendingGpsCoords.longitude.toFixed(6) +
                       "\nAccuracy: " + (pendingGpsCoords.accuracy || 'N/A') + "m";
            }
            
            alert(msg);
        });
        
        $('body').append($indicator);
        updateGpsStatusIndicator();
    }

    function updateGpsStatusIndicator() {
        var $text = $('#grt_gps_status_text');
        if (!$text.length) return;
        
        if (gpsStatus === "success" && pendingGpsCoords) {
            $text.text('Active ✓').css('color', '#28a745');
            $('#grt_gps_status_indicator').css('background', 'rgba(40, 167, 69, 0.9)');
        } else if (gpsStatus === "capturing") {
            $text.text('Capturing...').css('color', '#ffc107');
            $('#grt_gps_status_indicator').css('background', 'rgba(255, 193, 7, 0.9)');
        } else if (gpsStatus === "failed") {
            $text.text('Failed ✗').css('color', '#dc3545');
            $('#grt_gps_status_indicator').css('background', 'rgba(220, 53, 69, 0.9)');
        } else {
            $text.text('Starting...').css('color', '#17a2b8');
            $('#grt_gps_status_indicator').css('background', 'rgba(23, 162, 184, 0.9)');
        }
    }

    // Add indicator when DOM ready
    $(document).ready(function() {
        setTimeout(addGpsStatusIndicator, 1000);
    });

    // Store GPS coordinates in memory for immediate use
    var pendingGpsCoords = null;
    var gpsCapturePending = false;
    var gpsStatus = "not_started"; // not_started, capturing, success, failed

    function captureGpsInBackground() {
        if (gpsCapturePending) {
            console.log("GRT GPS: Capture already in progress, skipping");
            return;
        }
        console.log("GRT GPS: Starting background GPS capture...");
        gpsCapturePending = true;
        gpsStatus = "capturing";
        updateGpsStatusIndicator();
        
        getCurrentPosition()
            .done(function (coords) {
                pendingGpsCoords = coords;
                gpsCapturePending = false;
                gpsStatus = "success";
                console.log("GRT GPS: Successfully captured coordinates:", coords.latitude, coords.longitude);
                pushGpsToServer(coords);
                updateGpsStatusIndicator();
            })
            .fail(function (reason) {
                gpsCapturePending = false;
                gpsStatus = "failed";
                console.error("GRT GPS: Failed to capture GPS:", reason);
                updateGpsStatusIndicator();
            });
    }

    // Pre-capture GPS on page load
    console.log("GRT GPS: Initializing GPS tracking module");
    setTimeout(function() {
        captureGpsInBackground();
    }, 2000); // Wait 2 seconds after page load
    
    // Re-capture every 60 seconds  
    setInterval(captureGpsInBackground, 60000);

    function processMailActivityRpc(params, options, callOriginal) {
        try {
            if (!params || params.model !== "mail.activity") {
                return callOriginal(params, options);
            }

            if (params.method === "create") {
                var normalized = normalizeCreateArgs(params.args);
                if (!normalized) {
                    return callOriginal(params, options);
                }

                console.log("GRT GPS: Creating CRM activity, GPS status:", gpsStatus, "Has coords:", !!pendingGpsCoords);
                var crmContext = isCrmCreateContext(params, normalized.valuesList);

                // Use cached GPS if available
                if (pendingGpsCoords) {
                    console.log("GRT GPS: Using cached coordinates:", pendingGpsCoords.latitude, pendingGpsCoords.longitude);
                    var updatedArgs = params.args.slice(0);
                    var updatedValuesList = injectCoordinates(normalized.valuesList, pendingGpsCoords, crmContext);
                    updatedArgs[0] = normalized.isList ? updatedValuesList : updatedValuesList[0];
                    
                    console.log("GRT GPS: Original params.args:", JSON.stringify(params.args));
                    console.log("GRT GPS: Updated args being sent:", JSON.stringify(updatedArgs));
                    
                    var updatedParams = Object.assign({}, params, {args: updatedArgs});
                    updatedParams = injectCreateGpsContext(updatedParams, pendingGpsCoords);
                    
                    console.log("GRT GPS: Final params being sent to RPC:", JSON.stringify(updatedParams));
                    
                    // Re-capture for next time (async, don't wait)
                    setTimeout(captureGpsInBackground, 100);
                    
                    return callOriginal(updatedParams, options);
                }

                // No GPS available - try to capture now with user feedback
                console.warn("GRT GPS: No cached GPS. Attempting immediate capture...");
                
                // Show a brief notification
                var $notification = $('<div class="o_notification_manager">' +
                    '<div class="o_notification_content">' +
                    '<div class="o_notification bg-info">' +
                    '<div class="o_close" style="cursor:pointer;">×</div>' +
                    '<div>Mencoba menangkap lokasi GPS...</div>' +
                    '</div></div></div>');
                $('body').append($notification);
                
                var notifTimeout = setTimeout(function() {
                    $notification.fadeOut(function() { $(this).remove(); });
                }, 3000);

                // Try immediate capture
                var deferred = $.Deferred();
                getCurrentPosition()
                    .done(function (coords) {
                        clearTimeout(notifTimeout);
                        $notification.find('.o_notification').removeClass('bg-info').addClass('bg-success')
                            .find('div:last').text('GPS berhasil: ' + coords.latitude.toFixed(6) + ', ' + coords.longitude.toFixed(6));
                        setTimeout(function() {
                            $notification.fadeOut(function() { $(this).remove(); });
                        }, 2000);
                        
                        pendingGpsCoords = coords;
                        pushGpsToServer(coords);
                        console.log("GRT GPS: Immediate capture successful:", coords.latitude, coords.longitude);
                        
                        var updatedArgs = params.args.slice(0);
                        var updatedValuesList = injectCoordinates(normalized.valuesList, coords, crmContext);
                        updatedArgs[0] = normalized.isList ? updatedValuesList : updatedValuesList[0];
                        var updatedParams = Object.assign({}, params, {args: updatedArgs});
                        updatedParams = injectCreateGpsContext(updatedParams, coords);
                        
                        callOriginal(updatedParams, options).then(function(result) {
                            deferred.resolve(result);
                        }).guardedCatch(function(error) {
                            deferred.reject(error);
                        });
                    })
                    .fail(function (reason) {
                        clearTimeout(notifTimeout);
                        $notification.find('.o_notification').removeClass('bg-info').addClass('bg-warning')
                            .find('div:last').text('GPS gagal: ' + reason);
                        setTimeout(function() {
                            $notification.fadeOut(function() { $(this).remove(); });
                        }, 4000);
                        
                        console.error("GRT GPS: Immediate capture failed:", reason);
                        showGpsWarning(_t("GPS tidak dapat diambil: ") + reason + _t(". Activity dibuat tanpa koordinat GPS."));
                        
                        callOriginal(params, options).then(function(result) {
                            deferred.resolve(result);
                        }).guardedCatch(function(error) {
                            deferred.reject(error);
                        });
                    });
                
                return deferred;
            }

            if (params.method === "action_feedback") {
                var ids = getActivityIds(params);
                if (!ids.length) {
                    return callOriginal(params, options);
                }

                console.log("GRT GPS: Marking activity done, GPS status:", gpsStatus, "Has coords:", !!pendingGpsCoords);

                // For action_feedback, inject GPS if available
                if (pendingGpsCoords) {
                    console.log("GRT GPS: Injecting GPS context for feedback:", pendingGpsCoords.latitude, pendingGpsCoords.longitude);
                    var updatedParams = injectGpsContext(params, pendingGpsCoords);
                    
                    // Re-capture for next time (async, don't wait)
                    setTimeout(captureGpsInBackground, 100);
                    
                    return callOriginal(updatedParams, options);
                }

                // No GPS, proceed without it
                console.warn("GRT GPS: No GPS available for feedback");
                setTimeout(captureGpsInBackground, 100); // Try to capture for next time
                return callOriginal(params, options);
            }

            return callOriginal(params, options);
        } catch (e) {
            console.error("GRT GPS: Process RPC error", e);
            return callOriginal(params, options);
        }
    }

    rpc.query = function (params, options) {
        try {
            return processMailActivityRpc(
                params,
                options,
                function (p, o) {
                    return originalQuery(p, o);
                }
            );
        } catch (e) {
            console.error("GRT GPS: RPC query error", e);
            return originalQuery(params, options);
        }
    };

    window.__grtGpsHookLoaded = true;
});
