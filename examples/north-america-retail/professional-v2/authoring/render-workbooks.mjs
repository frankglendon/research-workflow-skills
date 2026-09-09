import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=process.argv[2]||root;
const books=JSON.parse(await fs.readFile(path.join(out,'workbook-data.json'),'utf8'));
const previews=path.join(out,'.previews'); await fs.mkdir(previews,{recursive:true});
const col=n=>String.fromCharCode(65+n);
const text=v=>typeof v==='string'&&v.startsWith('=')?"'"+v:v;
for(const [name,tabs] of Object.entries(books)){
 const wb=Workbook.create();
 for(const t of tabs){
  const sh=wb.worksheets.add(t.name); sh.showGridLines=false;
  const values=[t.headers,...t.rows].map(r=>r.map(text)),end=col(t.headers.length-1);
  const used=sh.getRange(`A1:${end}${values.length}`); used.values=values;
  used.format.font={name:'Hiragino Sans GB',size:11,color:'#23313F'};
  used.format.wrapText=true; used.format.verticalAlignment='top';
  sh.getRange(`A1:${end}1`).format={fill:'#16384D',font:{name:'Hiragino Sans GB',size:11,bold:true,color:'#FFFFFF'},rowHeight:36};
  t.widths.forEach((w,i)=>sh.getRange(`${col(i)}1:${col(i)}${values.length}`).format.columnWidthPx=w);
  sh.freezePanes.freezeRows(1); sh.freezePanes.freezeColumns(t.headers.length>3?2:1);
  for(let i=0;i<t.rows.length;i++){
   const row=sh.getRange(`A${i+2}:${end}${i+2}`),kind=t.kinds[String(i)];
   const height=Math.max(29,...t.rows[i].map((v,j)=>Math.ceil([...String(v||'')].reduce((n,c)=>n+(c.charCodeAt(0)>255?1:.55),0)/Math.max(6,t.widths[j]/15))*18+12));
   row.format.rowHeight=height;
   if(kind==='module')row.format={fill:'#16384D',font:{name:'Hiragino Sans GB',size:13,bold:true,color:'#FFFFFF'},rowHeight:34};
   else if(kind==='question')row.format={fill:'#DDF1F3',font:{name:'Hiragino Sans GB',size:11,bold:true,color:'#113B4D'}};
   else if(i%2===1)row.format.fill='#F5F7F8';
  }
  const ranges=[`A1:${end}${Math.min(12,values.length)}`];
  if(t.name==='03 主问卷')for(const r of [250,570,810])ranges.push(`A${r}:${end}${r+12}`);
  for(let i=0;i<ranges.length;i++){
   const b=await wb.render({sheetName:t.name,range:ranges[i],scale:1.2,format:'png'});
   await fs.writeFile(path.join(previews,`${name}-${t.name.split(' ')[0]}-${i}.png`),new Uint8Array(await b.arrayBuffer()));
  }
 }
 const x=await SpreadsheetFile.exportXlsx(wb); await x.save(path.join(out,name+'.xlsx'));
 console.log(JSON.stringify({name,sheets:tabs.length,output:path.join(out,name+'.xlsx')}));
}
