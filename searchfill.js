var inputs = document.querySelectorAll("input");
var mainInput = null;
var companyInput = null;
for(var i=0;i<inputs.length;i++){
  var inp = inputs[i];
  if(inp.placeholder && inp.placeholder.indexOf("关键词") >= 0){
    mainInput = inp;
  }
  if(inp.id && inp.id.indexOf("compSearchType") >= 0){
    companyInput = inp;
  }
}
// First, set main search value via native input + dispatch events
mainInput.value = "北京 车险精算 GLM Python SQL 60-90万";
mainInput.dispatchEvent(new Event('input', {bubbles:true}));
mainInput.dispatchEvent(new Event('change', {bubbles:true}));
mainInput.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', bubbles:true}));
"done:" + mainInput.id + " value=" + mainInput.value
