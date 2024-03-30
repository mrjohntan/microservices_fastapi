import fs from 'fs';
import starumlWatermarkRemover from 'staruml-watermark-remover';

const svg = fs.readFileSync('input.svg', 'utf8');

fs.writeFileSync('output.svg', starumlWatermarkRemover(svg));