// Renders the cards that `python3 tools/og.py --html DIR` wrote, for workspaces with Node Playwright but no Python Playwright.
// Same steps as og.py's render(): load the card, run FIT once the fonts are ready, save a JPEG at quality 88.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = process.argv[2];
  const { fit, jobs } = JSON.parse(fs.readFileSync(path.join(dir, 'jobs.json'), 'utf8'));
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1200, height: 630 } });
  for (const j of jobs) {
    await pg.setContent(fs.readFileSync(j.html, 'utf8'));
    await pg.evaluate('(' + fit + ')()');
    await pg.waitForTimeout(200);
    await pg.screenshot({ path: j.out, type: 'jpeg', quality: 88 });
    console.log('wrote', j.out);
  }
  await b.close();
})();
