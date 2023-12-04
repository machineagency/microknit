

function drawChart(canvas) {
  const ctx = canvas.getContext("2d");
  let symbolLineWidth = 3;

  ctx.lineWidth = 0.01 * symbolLineWidth;

  ctx.resetTransform();
  ctx.translate(-0.5, -0.5);

  for (let y = 0; y < GLOBAL_STATE.chart.height; y++) {
    for (let x = 0; x < GLOBAL_STATE.chart.width; x++) {
      let paletteIndex = GLOBAL_STATE.chart.pixel(x, y);

      const symbol = DEFAULT_SYMBOLS[paletteIndex];
      ctx.save();
      ctx.translate(
        x * GLOBAL_STATE.scale,
        (GLOBAL_STATE.chart.height - y - 1) * GLOBAL_STATE.scale
      );
      ctx.scale(GLOBAL_STATE.scale, GLOBAL_STATE.scale);

      let yarnPaletteIndex =
        GLOBAL_STATE.yarnSequence[
          (GLOBAL_STATE.chart.height - y - 1) % GLOBAL_STATE.yarnSequence.length
        ];

      ctx.fillStyle = GLOBAL_STATE.yarnPalette[yarnPaletteIndex];
      ctx.fillRect(0, 0, 1, 1);

      if (SYMBOL_BITS[symbol]) {
        ctx.fillStyle = "#fff";
        ctx.fillRect(0, 0, 1, 1);
      }

      ctx.stroke(SYMBOL_PATHS[symbol]);

      ctx.restore();
    }
  }
}


// function sizeCanvases(canvases) {
//   canvases.forEach((canvas) => {
//     canvas.width = GLOBAL_STATE.chart.width * GLOBAL_STATE.scale;
//     canvas.height = GLOBAL_STATE.chart.height * GLOBAL_STATE.scale;

//     canvas.style.width = `${
//       (GLOBAL_STATE.chart.width * GLOBAL_STATE.scale) / devicePixelRatio
//     }px`;
//     canvas.style.height = `${
//       (GLOBAL_STATE.chart.height * GLOBAL_STATE.scale) / devicePixelRatio
//     }px`;
//   });
// }

// function highlightRow() {
//   const ctx = overlayCanvas.getContext("2d");
//   ctx.resetTransform();

//   ctx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
//   ctx.translate(-0.5, -0.5);
//   const row = GLOBAL_STATE.currentRow;
//   console.log(row);
//   ctx.strokeStyle = "green";
//   ctx.lineWidth = 3;

//   ctx.strokeRect(
//     0,
//     (GLOBAL_STATE.chart.height - row - 1) * GLOBAL_STATE.scale,
//     GLOBAL_STATE.chart.width * GLOBAL_STATE.scale,
//     GLOBAL_STATE.scale
//   );
// }
