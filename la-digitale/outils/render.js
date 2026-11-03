const { chromium } = require('playwright');
const { spawn } = require('child_process');
const [,, W, H, fps, secs, out, preview] = process.argv;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +W, height: +H } });
  await p.goto('file://' + __dirname + '/scene.html');
  await p.evaluate(([w, h]) => init(w, h), [+W, +H]);
  if (preview) { for (const t of [0, 7]) { await p.evaluate(t => draw(t), t); await p.locator('canvas').screenshot({ path: `${out}_t${t}.png` }); } await b.close(); return; }
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', fps, '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const N = +fps * +secs;
  for (let i = 0; i < N; i++) {
    const d = await p.evaluate(t => { draw(t); return document.getElementById('c').toDataURL('image/jpeg', 0.95); }, i / +fps);
    if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
})();
