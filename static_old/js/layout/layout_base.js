/**
 * Created by mahmudul on 2/11/14.
 */

/*
 * URL Utils - v1.11 - 9/10/2009
 * http://benalman.com/
 *
 * Copyright (c) 2009 "Cowboy" Ben Alman
 * Licensed under the MIT license
 * http://benalman.com/about/license/
 */
/*
 * jQuery BBQ: Back Button & Query Library - v1.2.1 - 2/17/2010
 * http://benalman.com/projects/jquery-bbq-plugin/
 *
 * Copyright (c) 2010 "Cowboy" Ben Alman
 * Dual licensed under the MIT and GPL licenses.
 * http://benalman.com/about/license/
 */
(function ($, p) {
    var i, m = Array.prototype.slice, r = decodeURIComponent, a = $.param, c, l, v, b = $.bbq = $.bbq || {}, q, u, j, e = $.event.special, d = "hashchange", A = "querystring", D = "fragment", y = "elemUrlAttr", g = "location", k = "href", t = "src", x = /^.*\?|#.*$/g, w = /^.*\#/, h, C = {};

    function E(F) {
        return typeof F === "string"
    }

    function B(G) {
        var F = m.call(arguments, 1);
        return function () {
            return G.apply(this, F.concat(m.call(arguments)))
        }
    }

    function n(F) {
        return F.replace(/^[^#]*#?(.*)$/, "$1")
    }

    function o(F) {
        return F.replace(/(?:^[^?#]*\?([^#]*).*$)?.*/, "$1")
    }

    function f(H, M, F, I, G) {
        var O, L, K, N, J;
        if (I !== i) {
            K = F.match(H ? /^([^#]*)\#?(.*)$/ : /^([^#?]*)\??([^#]*)(#?.*)/);
            J = K[3] || "";
            if (G === 2 && E(I)) {
                L = I.replace(H ? w : x, "")
            } else {
                N = l(K[2]);
                I = E(I) ? l[H ? D : A](I) : I;
                L = G === 2 ? I : G === 1 ? $.extend({}, I, N) : $.extend({}, N, I);
                L = a(L);
                if (H) {
                    L = L.replace(h, r)
                }
            }
            O = K[1] + (H ? "#" : L || !K[1] ? "?" : "") + L + J
        } else {
            O = M(F !== i ? F : p[g][k])
        }
        return O
    }

    a[A] = B(f, 0, o);
    a[D] = c = B(f, 1, n);
    c.noEscape = function (G) {
        G = G || "";
        var F = $.map(G.split(""), encodeURIComponent);
        h = new RegExp(F.join("|"), "g")
    };
    c.noEscape(",/");
    $.deparam = l = function (I, F) {
        var H = {}, G = {"true": !0, "false": !1, "null": null};
        $.each(I.replace(/\+/g, " ").split("&"), function (L, Q) {
            var K = Q.split("="), P = r(K[0]), J, O = H, M = 0, R = P.split("]["), N = R.length - 1;
            if (/\[/.test(R[0]) && /\]$/.test(R[N])) {
                R[N] = R[N].replace(/\]$/, "");
                R = R.shift().split("[").concat(R);
                N = R.length - 1
            } else {
                N = 0
            }
            if (K.length === 2) {
                J = r(K[1]);
                if (F) {
                    J = J && !isNaN(J) ? +J : J === "undefined" ? i : G[J] !== i ? G[J] : J
                }
                if (N) {
                    for (; M <= N; M++) {
                        P = R[M] === "" ? O.length : R[M];
                        O = O[P] = M < N ? O[P] || (R[M + 1] && isNaN(R[M + 1]) ? {} : []) : J
                    }
                } else {
                    if ($.isArray(H[P])) {
                        H[P].push(J)
                    } else {
                        if (H[P] !== i) {
                            H[P] = [H[P], J]
                        } else {
                            H[P] = J
                        }
                    }
                }
            } else {
                if (P) {
                    H[P] = F ? i : ""
                }
            }
        });
        return H
    };
    function z(H, F, G) {
        if (F === i || typeof F === "boolean") {
            G = F;
            F = a[H ? D : A]()
        } else {
            F = E(F) ? F.replace(H ? w : x, "") : F
        }
        return l(F, G)
    }

    l[A] = B(z, 0);
    l[D] = v = B(z, 1);
    $[y] || ($[y] = function (F) {
        return $.extend(C, F)
    })({a: k, base: k, iframe: t, img: t, input: t, form: "action", link: k, script: t});
    j = $[y];
    function s(I, G, H, F) {
        if (!E(H) && typeof H !== "object") {
            F = H;
            H = G;
            G = i
        }
        return this.each(function () {
            var L = $(this), J = G || j()[(this.nodeName || "").toLowerCase()] || "", K = J && L.attr(J) || "";
            L.attr(J, a[I](K, H, F))
        })
    }

    $.fn[A] = B(s, A);
    $.fn[D] = B(s, D);
    b.pushState = q = function (I, F) {
        if (E(I) && /^#/.test(I) && F === i) {
            F = 2
        }
        var H = I !== i, G = c(p[g][k], H ? I : {}, H ? F : 2);
        p[g][k] = G + (/#/.test(G) ? "" : "#")
    };
    b.getState = u = function (F, G) {
        return F === i || typeof F === "boolean" ? v(F) : v(G)[F]
    };
    b.removeState = function (F) {
        var G = {};
        if (F !== i) {
            G = u();
            $.each($.isArray(F) ? F : arguments, function (I, H) {
                delete G[H]
            })
        }
        q(G, 2)
    };
    e[d] = $.extend(e[d], {
        add: function (F) {
            var H;

            function G(J) {
                var I = J[D] = c();
                J.getState = function (K, L) {
                    return K === i || typeof K === "boolean" ? l(I, K) : l(I, L)[K]
                };
                H.apply(this, arguments)
            }

            if ($.isFunction(F)) {
                H = F;
                return G
            } else {
                H = F.handler;
                F.handler = G
            }
        }
    })
})(jQuery, this);

/*
 * jQuery hashchange event - v1.2 - 2/11/2010
 * http://benalman.com/projects/jquery-hashchange-plugin/
 *
 * Copyright (c) 2010 "Cowboy" Ben Alman
 * Dual licensed under the MIT and GPL licenses.
 * http://benalman.com/about/license/
 */
(function ($, i, b) {
    var j, k = $.event.special, c = "location", d = "hashchange", l = "href", f = $.browser, g = document.documentMode, h = f.msie && (g === b || g < 8), e = "on" + d in i && !h;

    function a(m) {
        m = m || i[c][l];
        return m.replace(/^[^#]*#?(.*)$/, "$1")
    }

    $[d + "Delay"] = 100;
    k[d] = $.extend(k[d], {
        setup: function () {
            if (e) {
                return false
            }
            $(j.start)
        }, teardown: function () {
            if (e) {
                return false
            }
            $(j.stop)
        }
    });
    j = (function () {
        var m = {}, r, n, o, q;

        function p() {
            o = q = function (s) {
                return s
            };
            if (h) {
                n = $('<iframe src="javascript:0"/>').hide().insertAfter("body")[0].contentWindow;
                q = function () {
                    return a(n.document[c][l])
                };
                o = function (u, s) {
                    if (u !== s) {
                        var t = n.document;
                        t.open().close();
                        t[c].hash = "#" + u
                    }
                };
                o(a())
            }
        }

        m.start = function () {
            if (r) {
                return
            }
            var t = a();
            o || p();
            (function s() {
                var v = a(), u = q(t);
                if (v !== t) {
                    o(t = v, u);
                    $(i).trigger(d)
                } else {
                    if (u !== t) {
                        i[c][l] = i[c][l].replace(/#.*/, "") + "#" + u
                    }
                }
                r = setTimeout(s, $[d + "Delay"])
            })()
        };
        m.stop = function () {
            if (!n) {
                r && clearTimeout(r);
                r = 0
            }
        };
        return m
    })()
})(jQuery, this);