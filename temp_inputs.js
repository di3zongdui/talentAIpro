// Find search-related elements
var inputs = document.querySelectorAll('input');
for (var i = 0; i < inputs.length; i++) {
  var el = inputs[i];
  var info = '[' + i + '] type=' + el.type + ' placeholder="' + (el.placeholder || '') + '" id="' + (el.id || '') + '" class="' + (el.className || '').substring(0, 80) + '"';
  console.log(info);
}
