const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+process.cwd()+'/guia.html');
await p.pdf({path:'../guia/Guia_de_preguntas_con_respuestas.pdf',format:'Letter',printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:8px;width:100%;text-align:center;color:#888">Guía de preguntas · ¿Quién Quiere Ser Sexperto? · <span class="pageNumber"></span>/<span class="totalPages"></span></div>',margin:{top:'16mm',bottom:'16mm',left:'14mm',right:'14mm'}});
await b.close();})();
