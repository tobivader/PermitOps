(function(){
  'use strict';
  const D=window.PERMITOPS_DATA,E=window.PermitOpsEngine,$=s=>document.querySelector(s);
  if(!D||!E){$('#report').innerHTML='<div class="error-state">Dashboard data could not load. Regenerate with python -m src.build_dashboard, then reload.</div>';return;}
  const C={blue:'#2165ff',teal:'#365e4c',amber:'#c58b37',pale:'#bad1ff',grid:'#e8eee8',text:'#7d9386'};
  const nf=new Intl.NumberFormat('en-CA',{maximumFractionDigits:1});
  const fmt=v=>v===null||v===undefined?'—':nf.format(v);
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const monthLabel=m=>new Date(m+'-01T12:00:00Z').toLocaleDateString('en-CA',{month:'short',year:'numeric',timeZone:'UTC'});
  const rangeLabel=(a,b)=>`${monthLabel(a)} – ${monthLabel(b)}`;
  const state={page:['overview','bottlenecks','workload'].includes(location.hash.slice(1))?location.hash.slice(1):'overview',start:D.meta.recentStart,end:D.meta.end,category:null};
  let exportRows=[];
  $('#start').min=$('#end').min=D.meta.start;$('#start').max=$('#end').max=D.meta.end;
  for(const [id,name] of D.categories.entries()){const option=document.createElement('option');option.value=id;option.textContent=name;$('#category').append(option);}
  function panel(title,subtitle,body,tag='',className=''){return `<article class="panel ${className}"><div class="panel-header"><div><h2>${title}</h2><p class="panel-subtitle">${subtitle}</p></div>${tag?`<span class="panel-tag">${tag}</span>`:''}</div><div class="panel-body">${body}</div></article>`;}
  function delta(current,prior,days=false){if(current===null||prior===null||prior===0)return 'No comparable prior value';const diff=days?current-prior:(current-prior)/prior*100;return `<span class="delta ${days?(diff<=0?'good':'warn'):''}">${diff>0?'↑':diff<0?'↓':'→'} ${fmt(Math.abs(diff))}${days?' days':'%'}</span> vs preceding period`;}
  function kpi(title,value,unit,note,icon){return `<article class="kpi"><div class="kpi-top">${title}<span class="kpi-icon" aria-hidden="true">${icon}</span></div><div class="kpi-value">${fmt(value)}${unit?`<small>${unit}</small>`:''}</div><div class="kpi-note">${note}</div></article>`;}
  function svg(w,h,content,label){return `<svg class="chart" viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(label)}">${content}</svg>`;}
  function lineChart(rows,keys,colors,labels){
    if(!rows.length||!rows.some(r=>keys.some(k=>r[k]!==null&&r[k]>0)))return '<div class="chart-empty">No eligible records in this selection.</div>';
    const w=590,h=235,l=42,r=12,t=12,b=29,pw=w-l-r,ph=h-t-b;
    const maximum=Math.max(...rows.flatMap(row=>keys.map(k=>row[k]||0))),max=maximum?maximum*1.15:1;
    let html='';for(let i=0;i<5;i++){const y=t+ph-i*ph/4;html+=`<line x1="${l}" y1="${y}" x2="${w-r}" y2="${y}" stroke="${C.grid}"/><text x="${l-9}" y="${y+3}" text-anchor="end">${fmt(max*i/4)}</text>`;}
    const x=i=>l+(rows.length===1?pw/2:i*pw/(rows.length-1)),y=v=>t+ph-(v/max)*ph;
    keys.forEach((key,k)=>{
      const segments=[];let segment=[];rows.forEach((row,i)=>{if(row[key]===null){if(segment.length)segments.push(segment);segment=[];}else segment.push([i,row[key]]);});if(segment.length)segments.push(segment);
      segments.forEach(points=>{html+=`<path d="${points.map(([i,v],j)=>`${j?'L':'M'}${x(i)},${y(v)}`).join(' ')}" fill="none" stroke="${colors[k]}" stroke-width="2.5" stroke-linejoin="round"/>`;});
      rows.forEach((row,i)=>{if(row[key]===null)return;html+=`<circle cx="${x(i)}" cy="${y(row[key])}" r="${rows.length>30?2:3.2}" fill="white" stroke="${colors[k]}" stroke-width="1.7"><title>${monthLabel(row.month)} · ${labels[k]}: ${fmt(row[key])}</title></circle>`;});
    });
    const interval=Math.max(1,Math.ceil(rows.length/6));rows.forEach((row,i)=>{if(i%interval===0||i===rows.length-1)html+=`<text x="${x(i)}" y="${h-5}" text-anchor="middle">${new Date(row.month+'-01T12:00Z').toLocaleDateString('en-CA',{month:'short',year:rows.length>14?'2-digit':undefined,timeZone:'UTC'})}</text>`;});
    return svg(w,h,html,labels.join(' and ')+' by complete calendar month');
  }
  function legend(items){return `<div class="legend">${items.map(([label,color])=>`<span><i style="background:${color}"></i>${label}</span>`).join('')}</div>`;}
  const short=s=>s.replace('Building Additions/Alterations','Additions / alterations').replace('Small Residential Projects','Small residential projects').replace('Demolition Folder (DM)','Demolition').replace('Drain and Site Service','Drain / site service');
  function bars(rows,key,color=C.blue,compare=false){
    if(!rows.length)return '<div class="chart-empty">No eligible categories in this selection.</div>';
    const w=500,step=compare?43:35,h=rows.length*step+23,l=164,r=65,top=9;
    const max=Math.max(1,...rows.map(row=>row[key]||0),...(compare?rows.map(row=>row.prior?.median||0):[]))*1.07;
    let html='';[0,.25,.5,.75,1].forEach(p=>{const x=l+(w-l-r)*p;html+=`<line x1="${x}" y1="0" x2="${x}" y2="${h-22}" stroke="${C.grid}"/>`;});
    rows.forEach((row,i)=>{const y=top+i*step;html+=`<text class="category-label" x="${l-12}" y="${y+10}" text-anchor="end">${esc(short(row.name))}</text>`;
      html+=`<rect x="${l}" y="${y}" rx="3" width="${(row[key]||0)/max*(w-l-r)}" height="${compare?11:14}" fill="${color}"><title>${esc(row.name)}: ${fmt(row[key])}</title></rect><text class="value" x="${l+(row[key]||0)/max*(w-l-r)+8}" y="${y+10}">${fmt(row[key])}</text>`;
      if(compare&&row.prior?.median!==null&&row.prior?.median!==undefined)html+=`<rect x="${l}" y="${y+15}" rx="2" width="${row.prior.median/max*(w-l-r)}" height="9" fill="${C.pale}"><title>Prior median: ${fmt(row.prior.median)} days</title></rect>`;
    });return svg(w,h,html,compare?'Current and prior category medians in calendar days':'Category comparison');
  }
  function scatter(rows){
    rows=rows.filter(row=>row.median!==null);if(!rows.length)return '<div class="chart-empty">No eligible issued records.</div>';
    const w=500,h=247,l=43,r=15,t=18,b=38,pw=w-l-r,ph=h-t-b;
    const maxX=Math.max(...rows.map(r=>r.issued))*1.18,maxY=Math.max(...rows.map(r=>r.median))*1.25;
    let html='';for(let i=0;i<5;i++){const y=t+ph-i*ph/4;html+=`<line x1="${l}" y1="${y}" x2="${w-r}" y2="${y}" stroke="${C.grid}"/><text x="${l-9}" y="${y+3}" text-anchor="end">${fmt(maxY*i/4)}</text>`;const x=l+i*pw/4;html+=`<text x="${x}" y="${h-19}" text-anchor="middle">${fmt(maxX*i/4)}</text>`;}
    rows.forEach(row=>{const x=l+row.issued/maxX*pw,y=t+ph-row.median/maxY*ph;html+=`<circle cx="${x}" cy="${y}" r="${row.name==='New Houses'?8:6}" fill="${row.name==='New Houses'?C.teal:C.blue}" fill-opacity=".75" stroke="white" stroke-width="2"><title>${esc(row.name)} · n=${fmt(row.issued)} · median ${fmt(row.median)} · P90 ${fmt(row.p90)}</title></circle>`;
      if(['New Houses','New Building','Small Residential Projects'].includes(row.name))html+=`<text x="${Math.min(x+10,w-105)}" y="${y-9}" class="value">${esc(short(row.name))}</text>`;});
    html+=`<text x="${l+pw/2}" y="${h-1}" text-anchor="middle">Issued records →</text><text transform="translate(11 ${t+ph/2}) rotate(-90)" text-anchor="middle">Median review days →</text>`;
    return svg(w,h,html,'Category issuance volume versus median review duration');
  }
  function table(headers,rows){return `<div class="table-scroll"><table><thead><tr>${headers.map(h=>`<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.length?rows.map(row=>`<tr>${row.map(cell=>`<td>${cell}</td>`).join('')}</tr>`).join(''):`<tr><td colspan="${headers.length}" class="empty-caption">No eligible records match this selection.</td></tr>`}</tbody></table></div>`;}
  function insight(title,text,button=''){return `<div class="insight-strip"><span class="insight-symbol" aria-hidden="true">↗</span><div><strong>${title}</strong><p>${text}</p></div>${button}</div>`;}
  function overview(){
    const s=E.metrics(D,state.start,state.end,state.category),pr=E.previous(state.start,state.end),p=pr.start>=D.meta.start?E.metrics(D,pr.start,pr.end,state.category):null;
    const rows=E.monthly(D,state.start,state.end,state.category),cats=E.categories(D,state.start,state.end,state.category),top=cats.filter(r=>r.issued>=100).slice(0,5);
    exportRows=[['Metric','Value'],['Applications',s.applications],['Issued records',s.issued],['Median review days',s.median],['P90 review days',s.p90]];
    const cards=`<div class="kpis">${kpi('Applications received',s.applications,'',p?delta(s.applications,p.applications):'Valid application dates in period','↗')}${kpi('Permits issued',s.issued,'',p?delta(s.issued,p.issued):'Eligible issued-review records','▤')}${kpi('Median review time',s.median,'days',p?delta(s.median,p.median,true):'Middle eligible issued case','◷')}${kpi('P90 review time',s.p90,'days',p?delta(s.p90,p.p90,true):'90th percentile of eligible reviews','◴')}</div>`;
    const demand=panel('Application & issuance trends','Different lifecycle cohorts · complete calendar months',legend([['Applications',C.teal],['Issued',C.blue]])+lineChart(rows,['applications','issued'],[C.teal,C.blue],['Applications','Issued'])+'<p class="chart-note">Volumes are eligible permit/revision counts. The two lines do not represent a conversion rate.</p>','Monthly');
    const reviews=panel('Review-time distribution over time','Median and P90 · valid issued cases',legend([['Median',C.blue],['P90',C.teal]])+lineChart(rows,['median','p90'],[C.blue,C.teal],['Median days','P90 days'])+'<p class="chart-note">Percentiles describe each issue cohort; unresolved cases are reported on Active workload.</p>','Calendar days');
    const focus=top[0];const action=focus?insight(`${esc(focus.name)} warrants a closer look`,`Median ${fmt(focus.median)} days · P90 ${fmt(focus.p90)} days across ${fmt(focus.issued)} issued records. Investigate case complexity, revisions and applicant response cycles before attributing delays.`,`<button class="text-link" data-goto="bottlenecks">Explore bottlenecks →</button>`):insight('Read the population before the number','This selection has fewer than 100 issued cases per category. Treat small-group results as descriptive.');
    const categoryTable=table(['Category','Issued records','Median days','P90 days','Median change','Readout'],top.map(row=>[
      `<button class="table-button" data-select="${row.id}">${esc(row.name)} ↗</button>`,fmt(row.issued),fmt(row.median),fmt(row.p90),row.change===null?'—':`${row.change>0?'+':''}${fmt(row.change)} days`,row.comparable?'<span class="pill blue">Comparable volume</span>':'<span class="pill amber">Limited baseline</span>']));
    return cards+`<div class="report-grid">${demand}${reviews}</div>`+focusText(p,pr)+action+`<article class="panel full-panel"><div class="panel-header"><div><h2>Where to focus next</h2><p class="panel-subtitle">Highest medians among categories with at least 100 selected-period issues · click a category to filter</p></div><span class="panel-tag">Investigation shortlist</span></div>${categoryTable}</article>`;
  }
  function focusText(prior,period){return prior?'':`<p class="chart-note" style="margin:-7px 0 18px">An equally long preceding period extends before the study begins. Prior-period changes are unavailable.</p>`;}
  function bottlenecks(){
    const cats=E.categories(D,state.start,state.end,state.category),s=E.metrics(D,state.start,state.end,state.category),valid=cats.filter(r=>r.issued>=100),worst=valid[0],comparable=valid.filter(r=>r.comparable),worsening=comparable.filter(r=>r.change>0).length;
    exportRows=[['Category','Issued','Median days','P90 days','Prior issued','Prior median days','Median change days'],...cats.map(r=>[r.name,r.issued,r.median,r.p90,r.prior?.issued,r.prior?.median,r.change])];
    const cards=`<div class="kpis">${kpi('Issued records in scope',s.issued,'','Valid completed review intervals','▤')}${kpi('Categories with ≥100 issues',valid.length,'','Volume qualifies the comparison','▦')}${kpi('Longest category median',worst?.median??null,'days',worst?esc(worst.name):'No category meets minimum volume','◷')}${kpi('Higher median vs prior',worsening,'categories','Among categories with ≥100 issues in both periods','↗')}</div>`;
    const plots=`<div class="report-grid">${panel('Category review-time comparison','Selected period versus equally long preceding period',legend([['Selected median',C.blue],['Prior median',C.pale]])+bars(valid.slice(0,7),'median',C.blue,true)+'<p class="chart-note">Ranked by selected-period median; minimum 100 issues. A category difference does not establish its cause.</p>','Calendar days')}${panel('Severity meets scale','Each dot is a category · hover for count and P90',legend([['Other categories',C.blue],['New Houses',C.teal]])+scatter(valid)+'<p class="chart-note">Long durations and meaningful volume help prioritize a case review, not a performance verdict.</p>','Issue cohorts')}</div>`;
    const reviewTable=table(['Category','Selected n','Prior n','Median','Prior median','P90','Change'],cats.filter(r=>r.issued>0).map(row=>[
      `<button class="table-button" data-select="${row.id}">${esc(row.name)}</button>`,fmt(row.issued),fmt(row.prior?.issued),`${fmt(row.median)} d`,`${fmt(row.prior?.median)} d`,`${fmt(row.p90)} d`,row.change===null?'—':`<span class="pill ${row.comparable?(row.change>0?'amber':'teal'):''}">${row.change>0?'+':''}${fmt(row.change)} d${row.comparable?'':' · small n'}</span>`]));
    const recent=D.revisions.filter(r=>r.period==='Recent'),total=recent.reduce((a,r)=>a+r.issued,0),tail=recent.reduce((a,r)=>a+r.over_365,0);
    const revisionTable=table(['Revision group','Issued','Median days','P90 days','Over 365 days'],recent.map(r=>[esc(r.revision_group),fmt(r.issued),fmt(r.median_days),fmt(r.p90_days),`${fmt(r.over_365)} (${fmt(r.over_365/r.issued*100)}%)`]));
    const dive=panel('Investigation spotlight · New Houses',`Fixed reference cohort: ${rangeLabel(D.meta.recentStart,D.meta.end)} · independent of page filters`,
      `<div class="mini-stats"><div>${fmt(total)}<small>issued records</small></div><div>${fmt(tail)}<small>reviews over 365 days</small></div><div>${fmt(total?tail/total*100:0)}%<small>share over 365 days</small></div></div><p class="callout">Are long durations concentrated in original permits or revisions? Compare both <strong>case counts and within-group tail rates</strong>; a larger count alone may reflect a larger group.</p>${revisionTable}<p class="chart-note">A revision interval is not the total duration of a construction project. Review issue-quarter patterns and application cohorts before inferring process change.</p>`, 'Revision analysis','deep-dive');
    return cards+plots+`<article class="panel full-panel"><div class="panel-header"><div><h2>Category evidence</h2><p class="panel-subtitle">Equal-length issue windows · differences are descriptive, not statistically adjusted</p></div></div>${reviewTable}</article>`+dive;
  }
  function workload(){
    const w=E.workload(D,state.category),share=w.active?w.unissued/w.active*100:0,old=w.bins['366+'],oldShare=w.unissued?old/w.unissued*100:0;
    exportRows=[['Category','Active','Unissued','Median unissued age','P90 unissued age','Oldest unissued age'],...w.categories.map(r=>[r.name,r.active,r.unissued,r.median,r.p90,r.oldest])];
    const cards=`<div class="kpis">${kpi('Active permits',w.active,'','All application years · current snapshot','▤')}${kpi('Active, unissued',w.unissued,'',`${fmt(share)}% of the eligible active workload`,'◷')}${kpi('Median unissued age',w.median,'days','Time since application, still unresolved','◴')}${kpi('P90 unissued age',w.p90,'days','Oldest tail of the current unissued queue','↗')}</div>`;
    const pct=w.active?w.withIssue/w.active:0,radius=57,circumference=2*Math.PI*radius;
    const donut=svg(190,165,`<circle cx="91" cy="79" r="${radius}" fill="none" stroke="#e8eef6" stroke-width="16"/><circle cx="91" cy="79" r="${radius}" fill="none" stroke="${C.teal}" stroke-width="16"/><circle cx="91" cy="79" r="${radius}" fill="none" stroke="${C.blue}" stroke-width="16" stroke-dasharray="${pct*circumference} ${circumference}" transform="rotate(-90 91 79)"/><text x="91" y="77" text-anchor="middle" style="font-size:23px;fill:#2a4561;font-weight:700">${fmt(pct*100)}%</text><text x="91" y="96" text-anchor="middle">with issue date</text>`,'Active workload split between issued and unissued');
    const composition=panel('Open does not always mean waiting for review','Active workload by issuance state',`<div class="donut-layout"><div style="width:49%">${donut}</div><div class="donut-legend"><p><i style="color:${C.blue}">●</i> With issue date<strong>${fmt(w.withIssue)}</strong></p><p><i style="color:${C.teal}">●</i> Unissued, valid age<strong>${fmt(w.unissued)}</strong></p>${w.active-w.withIssue-w.unissued?`<p>Other / invalid age<strong>${fmt(w.active-w.withIssue-w.unissued)}</strong></p>`:''}</div></div><p class="chart-note">Issued active cases typically remain open through construction and inspection. Do not treat this whole population as an initial-review queue.</p>`,'Snapshot');
    const ageRows=Object.entries(w.bins).filter(([name,n])=>name!=='Unknown'||n>0),max=Math.max(1,...ageRows.map(([,n])=>n));
    let ageSvg='';const barWidth=58,gap=28,left=37,base=183;for(let i=0;i<4;i++){const y=base-i*52;ageSvg+=`<line x1="${left}" x2="520" y1="${y}" y2="${y}" stroke="${C.grid}"/>`;}
    ageRows.forEach(([name,n],i)=>{const x=left+12+i*(barWidth+gap),height=n/max*147;ageSvg+=`<rect x="${x}" y="${base-height}" width="${barWidth}" height="${height}" rx="4" fill="${name==='366+'?C.amber:C.teal}"><title>${name} days: ${fmt(n)} unissued records</title></rect><text class="value" x="${x+barWidth/2}" y="${base-height-9}" text-anchor="middle">${fmt(n)}</text><text x="${x+barWidth/2}" y="${base+22}" text-anchor="middle">${name}</text>`;});
    const ages=panel('How old is the unissued queue?','Calendar days since application · eligible unissued cases',svg(530,230,ageSvg,'Unissued permit age bucket counts')+'<p class="chart-note">Age is elapsed time so far. These are not completed review durations or evidence of a breached SLA.</p>','Application age');
    const oldest=w.categories.filter(r=>r.unissued).sort((a,b)=>b.oldest-a.oldest);
    const rows=table(['Category','Unissued','Median age','P90 age','Oldest age','Review focus'],oldest.map(r=>[
      `<button class="table-button" data-select="${r.id}">${esc(r.name)}</button>`,fmt(r.unissued),`${fmt(r.median)} d`,`${fmt(r.p90)} d`,`${fmt(r.oldest)} d`,r.unissued>=100?'<span class="pill amber">Review aged cases</span>':'<span class="pill">Small population</span>']));
    return cards+`<div class="report-grid two-equal">${composition}${ages}</div>`+insight(`${fmt(old)} unissued records are older than one year`,`${fmt(oldShare)}% of the selected unissued queue is aged 366+ days. Validate case status and applicant response history before assigning a workflow intervention.`)+`<article class="panel full-panel"><div class="panel-header"><div><h2>Oldest unresolved categories</h2><p class="panel-subtitle">Sorted by oldest unissued application · validate old status records before acting</p></div><span class="panel-tag">Snapshot · ${D.meta.asOf}</span></div>${rows}</article>`;
  }
  function render(){
    const pages={overview:['01','Executive overview','A clear view of permit demand, review time and where to focus next.'],bottlenecks:['02','Bottleneck analysis','Compare duration, volume and change. Build an evidence-backed investigation shortlist.'],workload:['03','Active workload','Separate open construction activity from applications still waiting for issuance.']},[n,title,description]=pages[state.page];
    document.title=`${title} · PermitOps`;$('#page-title').textContent=title;$('#page-number').textContent='/ '+n;$('#page-description').textContent=description;
    document.querySelectorAll('[data-page]').forEach(button=>{button.classList.toggle('active',button.dataset.page===state.page);button.setAttribute('aria-current',button.dataset.page===state.page?'page':'false');});
    const snapshot=state.page==='workload';$('#period').disabled=snapshot;document.querySelectorAll('.custom-range').forEach(node=>node.classList.toggle('hidden',snapshot||$('#period').value!=='custom'));
    $('#start').value=state.start;$('#end').value=state.end;
    $('#date-label').textContent=snapshot?`Snapshot · ${D.meta.asOf} · all application years`:rangeLabel(state.start,state.end);
    $('#notice').textContent='';$('#export').disabled=false;
    if(state.start>state.end||state.start<D.meta.start||state.end>D.meta.end){$('#notice').textContent='Choose a valid complete-month range from January 2018 through '+monthLabel(D.meta.end)+'.';$('#report').innerHTML='<div class="chart-empty">Update the reporting period to view results.</div>';$('#export').disabled=true;return;}
    try{$('#report').innerHTML=state.page==='overview'?overview():state.page==='bottlenecks'?bottlenecks():workload();}catch(error){$('#report').innerHTML='<div class="error-state">Unable to calculate this selection. Reload the report or reset filters.</div>';console.error(error);}
    document.querySelectorAll('[data-select]').forEach(button=>button.addEventListener('click',()=>{state.category=Number(button.dataset.select);$('#category').value=String(state.category);render();window.scrollTo({top:0,behavior:'smooth'});}));
    document.querySelectorAll('[data-goto]').forEach(button=>button.addEventListener('click',()=>navigate(button.dataset.goto)));
  }
  function navigate(page){state.page=page;history.replaceState(null,'','#'+page);render();window.scrollTo({top:0,behavior:'smooth'});}
  document.querySelectorAll('[data-page]').forEach(button=>button.addEventListener('click',()=>navigate(button.dataset.page)));
  $('#category').addEventListener('change',()=>{state.category=$('#category').value==='all'?null:Number($('#category').value);render();});
  $('#period').addEventListener('change',()=>{const value=$('#period').value;if(value!=='custom'){state.start=value==='all'?D.meta.start:E.monthShift(D.meta.end,1-Number(value));state.end=D.meta.end;}render();});
  for(const id of ['start','end'])$('#'+id).addEventListener('change',()=>{state[id]=$('#'+id).value;render();});
  $('#reset').addEventListener('click',()=>{state.start=D.meta.recentStart;state.end=D.meta.end;state.category=null;$('#category').value='all';$('#period').value='12';render();});
  $('#methodology').addEventListener('click',()=>$('#definitions').showModal());$('#close-dialog').addEventListener('click',()=>$('#definitions').close());
  $('#definitions').addEventListener('click',event=>{if(event.target===$('#definitions'))$('#definitions').close();});
  $('#export').addEventListener('click',()=>{const rows=[['PermitOps view',state.page],['Snapshot',D.meta.asOf],['Category',state.category===null?'All':D.categories[state.category]],['Period',state.page==='workload'?'All application years':state.start+' through '+state.end],[],...exportRows];const csv=rows.map(row=>row.map(value=>'"'+String(value??'').replace(/"/g,'""')+'"').join(',')).join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8;'}));const a=document.createElement('a');a.href=url;a.download=`PermitOps_${state.page}_${D.meta.asOf}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  window.addEventListener('hashchange',()=>{if(['overview','bottlenecks','workload'].includes(location.hash.slice(1))){state.page=location.hash.slice(1);render();}});
  render();
})();
