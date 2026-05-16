const inputs = Array.from(document.querySelectorAll('input'));
const searchRelated = inputs.filter(i => 
  i.placeholder || 
  i.className.toLowerCase().includes('search') || 
  i.className.toLowerCase().includes('keyword') ||
  i.className.toLowerCase().includes('query') ||
  i.id.toLowerCase().includes('search') ||
  i.id.toLowerCase().includes('keyword')
);
searchRelated.forEach((i, idx) => {
  console.log(`[${idx}] id=${i.id} placeholder=${i.placeholder} class=${i.className} type=${i.type} name=${i.name}`);
});
console.log('---');
const allInputsInfo = inputs.map((i, idx) => ({
  idx,
  placeholder: i.placeholder || '',
  type: i.type,
  className: (i.className || '').substring(0, 60)
}));
allInputsInfo.filter(i => i.placeholder || i.className).slice(0, 20).forEach(i => {
  console.log(`[${i.idx}] type=${i.type} placeholder="${i.placeholder}" class="${i.className}"`);
});
