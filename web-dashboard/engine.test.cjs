const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const E=require('./engine.js');
const context={window:{}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'data.js'),'utf8'),context);
const data=context.window.PERMITOPS_DATA;
const refs=JSON.parse(fs.readFileSync(path.join(__dirname,'../outputs/dashboard_sql_reference.json')));
const near=(actual,expected)=>expected===null?assert.equal(actual,null):assert.ok(Math.abs(actual-expected)<1e-7,`${actual} != ${expected}`);
test('weighted percentiles interpolate at record ranks rather than averaging groups',()=>{
  assert.equal(E.percentile([[0,1],[10,1],[20,1],[40,1],[100,1]],.9),76);
  assert.equal(E.percentile([[0,9],[100,1]],.5),0);
  near(E.percentile([[0,9],[100,1]],.9),10);
  assert.equal(E.percentile([],.5),null);
});
for(const ref of refs)test(`filtered browser metrics equal PostgreSQL: ${ref.start}–${ref.end}, ${ref.category||'All'}`,()=>{
  const category=ref.category===null?null:data.categories.indexOf(ref.category);
  if(category!==null)assert.ok(category>=0);
  const actual=E.metrics(data,ref.start,ref.end,category);
  for(const key of ['issued','applications','median','p90'])near(actual[key],ref[key]);
});
test('all workload categories match independent SQL count and age references',()=>{
  for(const ref of data.activeReference){
    const actual=E.workload(data,data.categories.indexOf(ref.permit_type));
    near(actual.active,ref.active);near(actual.unissued,ref.unissued);
    near(actual.median,ref.median_age);near(actual.p90,ref.p90_age);
    near(actual.categories[0].oldest,ref.oldest);
  }
  const all=E.workload(data);assert.equal(Object.values(all.bins).reduce((a,n)=>a+n,0),all.unissued);
});
test('equal prior windows retain exact month boundaries',()=>{
  assert.deepEqual(E.previous('2025-11','2026-10'),{start:'2024-11',end:'2025-10'});
  assert.deepEqual(E.previous('2026-10','2026-10'),{start:'2026-09',end:'2026-09'});
});
