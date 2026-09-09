import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {Presentation,PresentationFile,FileBlob} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.resolve(process.argv[2]||root);
const buildRoot=path.join(out,'.build'); await fs.mkdir(buildRoot,{recursive:true});
const build=await fs.mkdtemp(path.join(buildRoot,'presentation-'));
const SKILL=process.env.PRESENTATIONS_SKILL_DIR; if(!SKILL) throw new Error('Set PRESENTATIONS_SKILL_DIR to the installed authoring skill.');
const PY=process.env.ARTIFACT_PYTHON; if(!PY) throw new Error('Set ARTIFACT_PYTHON to an absolute Python executable.');
if(!process.env.RUNTIME_NODE_MODULES) throw new Error('Set RUNTIME_NODE_MODULES to the configured artifact runtime.');
const {resolvePresentationFont,applyPresentationChartFont,finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const FONT=resolvePresentationFont({fontFamily:'Hiragino Sans GB'});
const contents=JSON.parse(await fs.readFile(path.join(out,'desk-research-content.json'),'utf8'));
const sources=JSON.parse(await fs.readFile(path.join(out,'sources.json'),'utf8'));
const pres=Presentation.create({slideSize:{width:1280,height:720}}),tableOwners=[],chartOwners=[];
function text(s,str,x,y,w,h,size=22,bold=false,color='#243849'){
 const t=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 t.text=String(str); t.text.style={typeface:FONT,fontSize:size,bold,color,autoFit:'none'}; return t;
}
for(const p of contents){
 const s=pres.slides.add(); s.background.fill=p.kind==='cover'?'#123A4E':'#FFFFFF';
 const cited=sources.filter(x=>p.source_ids.includes(x.id));
 s.speakerNotes.textFrame.setText([p.interpretation,...cited.map(x=>`${x.id} ${x.title}\n${x.url}\n发布：${x.published_at}；访问：${x.retrieved_at}\n口径：${x.scope}`),'断言编号：'+p.claim_ids.join(', '),'研究判断：'+p.decision].join('\n\n'));
 if(p.kind==='cover'){
  text(s,'北美零售研究  /  DESK RESEARCH',72,80,1136,50,21,false,'#8EDBE2');
  text(s,p.title,72,214,1136,150,52,true,'#FFFFFF');
  p.body.forEach((b,i)=>text(s,b,76,398+i*47,1120,42,24,false,'#FFFFFF'));
  text(s,p.decision,76,649,1120,40,15,false,'#B6D5DF'); continue;
 }
 text(s,p.section,60,23,1120,32,17,true,'#008D9B');
 text(s,p.title,60,68,1160,108,33,true,'#153B4F');
 if(p.kind==='table'){
  const values=[p.headers,...p.body],n=values.length,cols=p.headers.length;
  const widths=cols===2?[240,920]:p.section==='来源索引'?[230,490,440]:[180,330,650];
  const t=s.tables.add({rows:n,columns:cols,left:60,top:190,width:1160,height:345,values,columnWidths:widths});
  t.borders.assign({style:'solid',fill:'#D8E4E8',width:0.65});
  for(let r=0;r<n;r++)for(let c=0;c<cols;c++){
   const cell=t.getCell(r,c); cell.fill=r===0?'#163E50':r%2===1?'#F2F7F8':'#FFFFFF';
   cell.text.style={typeface:FONT,fontSize:p.section==='来源索引'?16:19,bold:r===0,color:r===0?'#FFFFFF':'#243849'};
  }
  tableOwners.push(p.number);
 }else if(p.kind==='chart'){
  const a=p.chart;
  const chart=s.charts.add('bar',{position:{left:64,top:194,width:730,height:325},categories:a.categories,series:[{name:a.series_name,values:a.values,valuesFormatCode:a.format,fill:'#009DAC'}],barOptions:{direction:'column',grouping:'clustered'},hasLegend:false,dataLabels:{showValue:true,position:'outEnd'},yAxis:{numberFormatCode:a.format},xAxis:{axisType:'textAxis'}});
  applyPresentationChartFont(chart,{fontFamily:FONT});
  text(s,a.unit,80,166,720,27,15,false,'#5C727F');
  p.body.forEach(([label,body],i)=>{text(s,label,848,190+i*119,365,32,20,true,'#008D9B');text(s,body,848,228+i*119,365,82,19);});
  text(s,p.chart_note,80,527,720,51,14,false,'#5B6A75');
  chartOwners.push(p.number);
 }else{
  const cols=p.body.length,w=1100/cols,gap=30;
  p.body.forEach(([label,body],i)=>{const x=60+i*(w+gap);text(s,label,x,213,w-10,47,25,true,'#008D9B');text(s,body,x,282,w-15,238,24);});
 }
 text(s,'研究含义',60,581,1150,28,16,true,'#008D9B');
 text(s,p.decision,60,615,1150,62,21,true,'#163B4D');
 text(s,p.section==='来源索引'?'资料检索截至 2026-09-09；完整链接与口径见幻灯片备注及 sources.json。':cited.length?cited.map(x=>`${x.id} ${x.publisher} ${x.published_at}`).join('  ·  '):p.interpretation,60,693,1100,20,11,false,'#657B85');
 text(s,String(p.number),1190,691,44,21,12,false,'#657B85');
}
const draft=path.join(build,'draft.pptx');
await(await PresentationFile.exportPptx(pres)).save(draft);
const dest=path.join(out,process.argv[3]||'desk-research.pptx');
const result=await finalizePresentation({workspaceDir:root,candidatePath:draft,finalPath:dest,pythonExecutable:PY,integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:tableOwners,requiredNativeChartOwnerSlides:chartOwners,materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:path.join(build,'validation.json')});
const preview=path.join(out,'.desk-previews'); await fs.mkdir(preview,{recursive:true});
const finalPres=await PresentationFile.importPptx(await FileBlob.load(dest));
for(let i=0;i<finalPres.slides.items.length;i++){
 const s=finalPres.slides.items[i],b=await finalPres.export({slide:s,format:'png',scale:1});
 await fs.writeFile(path.join(preview,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await b.arrayBuffer()));
 const layout=await s.export({format:'layout'}); await fs.writeFile(path.join(build,`slide-${i+1}.layout.json`),await layout.text());
}
console.log(JSON.stringify({file:dest,slides:contents.length,native_tables:tableOwners,native_charts:chartOwners,result}));
