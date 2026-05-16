var all = document.querySelectorAll("input");
var r = [...all].map(function(e){return e.id+"|"+(e.placeholder||"")+"|cls:"+(e.className||"").slice(0,30)}).join("\n");
r
