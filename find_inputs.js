(() => {
  var all = document.querySelectorAll("input,textarea,[contenteditable=true]");
  return [...all].map((e,i) => i + "|" + e.id + "|" + (e.placeholder||"") + "|" + (e.className||"").slice(0,50) + "|" + (e.value||"").slice(0,30)).join("\n");
})()
