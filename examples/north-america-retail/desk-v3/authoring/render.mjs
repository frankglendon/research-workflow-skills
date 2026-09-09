import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {Presentation,PresentationFile,FileBlob} from '@oai/artifact-tool';
const work=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(work,'../../../..');
const out=path.resolve(process.argv[2]||path.join(root,'outputs/desk-v3'));
await fs.mkdir(path.join(root,'.build'),{recursive:true});
await fs.mkdir(out,{recursive:true});
const build=await fs.mkdtemp(path.join(root,'.build/desk-v3-'));
const SKILL=process.env.PRESENTATION_SKILL_DIR;
const PY=process.env.RUNTIME_PYTHON;
if(!SKILL||!PY||!process.env.RUNTIME_NODE_MODULES)throw new Error('Set PRESENTATION_SKILL_DIR, RUNTIME_PYTHON and RUNTIME_NODE_MODULES from the installed presentation skill.');
const {resolvePresentationFont,applyPresentationChartFont,finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const FONT=resolvePresentationFont({fontFamily:'Hiragino Sans GB'});
const content=JSON.parse(await fs.readFile(path.join(work,'../desk-research-content.json'),'utf8'));
const sources=JSON.parse(await fs.readFile(path.join(work,'../sources.json'),'utf8'));
const pres=Presentation.create({slideSize:{width:1280,height:720}}),tables=[],charts=[];
function txt(s,value,x,y,w,h,size=22,bold=false,color='#243849'){
 const t=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 t.text=value;t.text.style={typeface:FONT,fontSize:size,bold,color,autoFit:'none'};return t;
}
for(const p of content){
 const s=pres.slides.add(),cited=sources.filter(x=>p.source_ids.includes(x.id));
 s.background.fill=p.kind==='cover'?'#173C4C':'#FFFFFF';
 const notes=[p.note,...cited.map(x=>`${x.id} ${x.publisher}: ${x.title}\n${x.url}\nPublished ${x.published_at}; accessed ${x.retrieved_at}\n${x.scope}`),`Claim IDs: ${p.claim_ids.join(', ')}`,`Analysis: ${p.implication}`];
 s.speakerNotes.textFrame.setText(notes.join('\n\n'));
 if(p.kind==='cover'){
  txt(s,'MINISO NORTH AMERICA',72,78,1136,40,23,true,'#78CBD2');
  txt(s,p.title,72,206,1136,180,53,true,'#FFFFFF');
  p.body.forEach((b,i)=>txt(s,b,76,420+i*47,1100,43,24,false,'#FFFFFF'));
  txt(s,p.implication,76,658,1130,35,15,false,'#BFD5DD');continue;
 }
 txt(s,p.section,60,20,1150,30,17,true,'#008D9B');
 txt(s,p.title,60,64,1160,100,34,true,'#173C4C');
 if(p.title.startsWith('Jellycat 用')){
  s.images.add({blob:new Uint8Array(await fs.readFile(path.join(work,'../assets/moon.jpg'))),contentType:'image/jpeg',alt:'Jellycat Amuseables Moon official product image',fit:'contain',position:{left:64,top:192,width:345,height:345}});
  txt(s,'Amuseables Moon\n美国站起价 US$33',72,546,330,55,20,true);
  p.body.forEach(([a,b,c],i)=>{const y=180+i*103;txt(s,a,450,y,760,32,23,true,'#008D9B');txt(s,b+'\n'+c,450,y+35,758,69,19.5);});
  const im=JSON.parse(await fs.readFile(path.join(work,'../assets/image-source.json'),'utf8'));s.speakerNotes.textFrame.setText(notes.join('\n\n')+'\nProduct photo: '+im.url);
 }else if(p.kind==='chart'){
  const a=p.chart;
  txt(s,a.unit,70,173,740,30,17,false,'#5C727F');
  const c=s.charts.add('bar',{position:{left:65,top:214,width:755,height:328},categories:a.categories,series:[{name:a.series_name,values:a.values,valuesFormatCode:a.format,fill:'#009DAC'}],barOptions:{direction:'column',grouping:'clustered'},hasLegend:false,dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:18,bold:true}},yAxis:{min:0,numberFormatCode:a.format==='0.00'?'0':a.format,textStyle:{fontSize:16}},xAxis:{axisType:'textAxis',textStyle:{fontSize:16}}});
  applyPresentationChartFont(c,{fontFamily:FONT});charts.push(p.number);
  p.body.forEach(([a,b],i)=>{txt(s,a,860,194+i*124,350,35,23,true,'#008D9B');txt(s,b,860,234+i*124,350,89,21);});
  if(p.note)txt(s,p.note,70,555,744,50,14,false,'#5C727F');
 }else{
  const values=[p.headers,...p.body],n=values.length;
  const widths=p.role==='sources'?[230,455,475]:[180,455,525];
  const t=s.tables.add({rows:n,columns:3,left:60,top:181,width:1160,height:409,values,columnWidths:widths});
  t.rows[0].height=44;
  for(let r=1;r<n;r++)t.rows[r].height=(409-44)/(n-1);
  t.borders.assign({style:'solid',fill:'#D6E3E7',width:0.6});
  for(let r=0;r<n;r++)for(let c=0;c<3;c++){
   const cell=t.getCell(r,c);cell.fill=r===0?'#173C4C':r%2?'#F2F7F8':'#FFFFFF';
   cell.text.style={typeface:FONT,fontSize:p.role==='sources'?15.5:21,bold:r===0||c===0,color:r===0?'#FFFFFF':'#243849'};
  }
  tables.push(p.number);
 }
 txt(s,p.implication,60,617,1155,62,22,true,'#173C4C');
 const footer=cited.map(x=>({run:`${x.id} ${x.publisher}  `,link:{uri:x.url,isExternal:true}}));
 txt(s,footer.length?[footer]:'独立分析；未主张品牌委托或机构背书',60,690,1110,20,11,false,'#607783');
 txt(s,String(p.number),1190,690,40,20,12,false,'#607783');
}
const draft=path.join(build,'draft.pptx');await(await PresentationFile.exportPptx(pres)).save(draft);
const dest=path.join(out,process.argv[3]||'MINISO-North-America-Desk-Research-v3.pptx');
const validation=await finalizePresentation({workspaceDir:root,candidatePath:draft,finalPath:dest,pythonExecutable:PY,integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...tables.flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:tables,requiredNativeChartOwnerSlides:charts,materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:path.join(build,'validation.json')});
console.log(JSON.stringify({stage:'finalized',slides:content.length,tables:tables.length,charts:charts.length,file:dest,build}));
const preview=path.join(build,'previews');await fs.mkdir(preview,{recursive:true});
const final=await PresentationFile.importPptx(await FileBlob.load(dest));
for(let i=0;i<final.slides.items.length;i++){
 const s=final.slides.items[i],b=await final.export({slide:s,format:'png',scale:1});
 await fs.writeFile(path.join(preview,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await b.arrayBuffer()));
 if(i%10===0)console.log(`preview ${i+1}/${content.length}`);
}
await fs.writeFile(path.join(build,'render-result.json'),JSON.stringify({file:dest,build,slides:content.length,tables,charts,validation},null,2));
console.log('Rendered all slides');
