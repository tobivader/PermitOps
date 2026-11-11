/* Exact, frequency-weighted analytics. Works in a browser and in Node tests. */
(function(root){
  'use strict';
  const number=v=>v===null||v===undefined?null:Number(v);
  function percentile(pairs,p){
    const sorted=pairs.filter(([x,n])=>x!==null&&n>0).map(([x,n])=>[Number(x),Number(n)]).sort((a,b)=>a[0]-b[0]);
    const n=sorted.reduce((s,[,c])=>s+c,0); if(!n)return null;
    const rank=(n-1)*p,lo=Math.floor(rank),hi=Math.ceil(rank);
    const at=k=>{let seen=0;for(const [value,count] of sorted){seen+=count;if(k<seen)return value;}return null;};
    return at(lo)+(at(hi)-at(lo))*(rank-lo);
  }
  function monthShift(month,amount){const [y,m]=month.split('-').map(Number);const date=new Date(Date.UTC(y,m-1+amount,1));return date.toISOString().slice(0,7);}
  function previous(start,end){const [sy,sm]=start.split('-').map(Number),[ey,em]=end.split('-').map(Number);const n=(ey-sy)*12+em-sm+1;return {start:monthShift(start,-n),end:monthShift(start,-1)};}
  function metrics(data,start,end,category=null){
    const selected=category===null?null:Number(category),hist=new Map();let issued=0,applications=0,over365=0;
    for(const [month,c,day,n] of data.reviews){if(month<start||month>end||(selected!==null&&c!==selected))continue;
      issued+=n;over365+=day>365?n:0;hist.set(day,(hist.get(day)||0)+n);}
    for(const [month,c,n] of data.applications){if(month>=start&&month<=end&&(selected===null||c===selected))applications+=n;}
    const pairs=[...hist];return {issued,applications,median:percentile(pairs,.5),p90:percentile(pairs,.9),over365};
  }
  function monthly(data,start,end,category=null){const result=[];for(let m=start;m<=end;m=monthShift(m,1))result.push({month:m,...metrics(data,m,m,category)});return result;}
  function categories(data,start,end,category=null){
    const prior=previous(start,end),validPrior=prior.start>=data.meta.start;
    return data.categories.map((name,id)=>{
      const current=metrics(data,start,end,id),baseline=validPrior?metrics(data,prior.start,prior.end,id):null;
      return {id,name,...current,prior:baseline,change:baseline&&current.median!==null&&baseline.median!==null?current.median-baseline.median:null,
              comparable:!!(baseline&&baseline.issued>=100&&current.issued>=100)};
    }).filter(row=>(category===null||row.id===Number(category))&&(row.issued||row.applications)).sort((a,b)=>(b.median??-1)-(a.median??-1)||b.issued-a.issued||a.name.localeCompare(b.name));
  }
  const ageBucket=age=>age===null?'Unknown':age<31?'0–30':age<91?'31–90':age<181?'91–180':age<366?'181–365':'366+';
  function workload(data,category=null){
    const selected=category===null?null:Number(category),bins={'0–30':0,'31–90':0,'91–180':0,'181–365':0,'366+':0,'Unknown':0};
    let active=0,unissued=0,withIssue=0;const ages=[],byCategory=new Map();
    for(const [c,age,n,u,i] of data.active){if(selected!==null&&c!==selected)continue;active+=n;unissued+=u;withIssue+=i;
      bins[ageBucket(age)]+=u;if(u&&age!==null)ages.push([age,u]);
      if(!byCategory.has(c))byCategory.set(c,{id:c,name:data.categories[c],active:0,unissued:0,ages:[],oldest:null});
      const row=byCategory.get(c);row.active+=n;row.unissued+=u;if(u&&age!==null){row.ages.push([age,u]);row.oldest=Math.max(row.oldest??0,age);}}
    return {active,unissued,withIssue,bins,median:percentile(ages,.5),p90:percentile(ages,.9),
      categories:[...byCategory.values()].map(row=>({...row,median:percentile(row.ages,.5),p90:percentile(row.ages,.9)})).sort((a,b)=>b.unissued-a.unissued)};
  }
  const api={percentile,monthShift,previous,metrics,monthly,categories,workload,ageBucket};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.PermitOpsEngine=api;
})(typeof window!=='undefined'?window:globalThis);
