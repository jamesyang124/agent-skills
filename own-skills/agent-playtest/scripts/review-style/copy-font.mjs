import { mkdirSync, copyFileSync } from 'node:fs';
const dest = '../../assets/review';
mkdirSync(`${dest}/fonts`, {recursive:true});
mkdirSync(`${dest}/licenses`, {recursive:true});
copyFileSync('node_modules/@fontsource-variable/inter/files/inter-latin-wght-normal.woff2', `${dest}/fonts/inter-latin-wght-normal.woff2`);
copyFileSync('node_modules/@fontsource-variable/inter/LICENSE', `${dest}/licenses/inter-LICENSE.txt`);
