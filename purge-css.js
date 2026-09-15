const { PurgeCSS } = require('purgecss');
const fs = require('fs');

const safelist = [
  // Bootstrap's own JS-driven states
  /^show/, /^fade/, /^collaps/, /^modal/, /^dropdown/, /^offcanvas/,
  'active', 'disabled', 'was-validated', 'is-invalid', 'is-valid', 'backdrop',
  // Your site's JS-driven states
  'scrolled', 'wow-visible', 'is-active', 'is-open', 'rooms-in',
  'hero-content-active', 'showing',
  /^wow/, /^fadeIn/, /^fadeOut/,
];

const content = [
  'templates/**/*.html',
];

async function run(inputFile, outputFile) {
  const result = await new PurgeCSS().purge({ content, css: [inputFile], safelist });
  fs.writeFileSync(outputFile, result[0].css);
  console.log(`✔ Purged: ${outputFile}`);
}

(async () => {
  await run(
    'static/tandu-main/css/bootstrap.min.css',
    'static/tandu-main/css/bootstrap.purged.css'
  );
  await run(
    'static/tandu-main/css/stylesheet.css',
    'static/tandu-main/css/stylesheet.purged.css'
  );
})();