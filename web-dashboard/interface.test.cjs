const {test}=require('node:test');
const assert=require('node:assert/strict');
const {JSDOM}=require('jsdom');
const fs=require('node:fs');const path=require('node:path');
function open(hash=''){
  const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
  const dom=new JSDOM(html,{runScripts:'outside-only',url:'https://example.test/'+hash});
  const errors=[];dom.window.console.error=e=>errors.push(String(e));dom.window.scrollTo=()=>{};
  for(const file of ['data.js','engine.js','app.js'])dom.window.eval(fs.readFileSync(path.join(__dirname,file),'utf8'));
  return {dom,w:dom.window,d:dom.window.document,errors};
}
test('executive page renders actual selected-period metrics and charts',()=>{
  const {dom,d,errors}=open();assert.equal(d.querySelector('h1').textContent,'Executive overview');
  assert.equal(d.querySelectorAll('.kpi').length,4);assert.ok(d.querySelectorAll('svg').length>=2);
  assert.ok(!d.querySelector('#report').textContent.includes('NaN'));assert.deepEqual(errors,[]);dom.window.close();
});
test('category filter recalculates the New Houses cohort instead of category averages',()=>{
  const {dom,w,d,errors}=open();const category=d.querySelector('#category');
  category.value=String(w.PERMITOPS_DATA.categories.indexOf('New Houses'));category.dispatchEvent(new w.Event('change'));
  const values=[...d.querySelectorAll('.kpi-value')].map(e=>e.textContent);
  assert.equal(values[1],'1,446');assert.equal(values[2],'52days');assert.equal(values[3],'419.5days');
  assert.deepEqual(errors,[]);dom.window.close();
});
test('page navigation renders bottlenecks and the fixed-cohort revision deep dive',()=>{
  const {dom,d,errors}=open();d.querySelector('[data-page="bottlenecks"]').click();
  assert.equal(d.querySelector('h1').textContent,'Bottleneck analysis');
  assert.match(d.querySelector('#report').textContent,/Investigation spotlight/);
  assert.match(d.querySelector('#report').textContent,/Original \(0\)/);assert.deepEqual(errors,[]);dom.window.close();
});
test('active workload ignores historical period controls but retains category filtering',()=>{
  const {dom,d,w,errors}=open('#workload');assert.equal(d.querySelector('#period').disabled,true);
  let values=[...d.querySelectorAll('.kpi-value')].map(e=>e.textContent);assert.equal(values[0],'194,325');assert.equal(values[1],'13,580');
  const cat=d.querySelector('#category');cat.value=String(w.PERMITOPS_DATA.categories.indexOf('Mechanical(MS)'));cat.dispatchEvent(new w.Event('change'));
  values=[...d.querySelectorAll('.kpi-value')].map(e=>e.textContent);assert.equal(values[1],'2,374');assert.deepEqual(errors,[]);dom.window.close();
});
test('custom month with applications and no issues has an explicit empty duration state',()=>{
  const {dom,d,w,errors}=open();const period=d.querySelector('#period');period.value='custom';period.dispatchEvent(new w.Event('change'));
  for(const id of ['start','end']){d.querySelector('#'+id).value='2024-12';d.querySelector('#'+id).dispatchEvent(new w.Event('change'));}
  const cat=d.querySelector('#category');cat.value=String(w.PERMITOPS_DATA.categories.indexOf('AS Alternative Solution'));cat.dispatchEvent(new w.Event('change'));
  const values=[...d.querySelectorAll('.kpi-value')].map(e=>e.textContent);assert.equal(values[0],'35');assert.equal(values[1],'0');assert.equal(values[2],'—days');
  assert.deepEqual(errors,[]);dom.window.close();
});
test('invalid date range is rejected and reset restores the default view',()=>{
  const {dom,d,w,errors}=open();const period=d.querySelector('#period');period.value='custom';period.dispatchEvent(new w.Event('change'));
  d.querySelector('#start').value='2026-10';d.querySelector('#start').dispatchEvent(new w.Event('change'));
  d.querySelector('#end').value='2025-01';d.querySelector('#end').dispatchEvent(new w.Event('change'));
  assert.equal(d.querySelector('#export').disabled,true);assert.match(d.querySelector('#notice').textContent,/valid/);
  d.querySelector('#reset').click();assert.equal(d.querySelectorAll('.kpi').length,4);assert.equal(d.querySelector('#export').disabled,false);assert.deepEqual(errors,[]);dom.window.close();
});
test('export prepares a CSV of the current filtered view',()=>{
  const {dom,d,w}=open('#workload');let blob,download;
  w.URL.createObjectURL=value=>{blob=value;return 'blob:test';};w.URL.revokeObjectURL=()=>{};
  w.HTMLAnchorElement.prototype.click=function(){download=this.download;};
  d.querySelector('#export').click();assert.equal(blob.type,'text/csv;charset=utf-8;');assert.match(download,/PermitOps_workload/);dom.window.close();
});
