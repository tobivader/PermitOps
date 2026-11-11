import {mkdirSync,copyFileSync,existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('.',import.meta.url));
mkdirSync(root+'dist',{recursive:true});
for(const name of ['index.html','styles.css','engine.js','app.js','data.js']){
  if(!existsSync(root+name))throw new Error('Missing '+name+'. Generate real data with python -m src.build_dashboard.');
  copyFileSync(root+name,root+'dist/'+name);
}
console.log('Built five static dashboard files.');
