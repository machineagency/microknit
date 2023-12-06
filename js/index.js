"use strict";
import { io } from "socket.io-client";
import { html, render } from "lit-html";
import pattern from "./pattern.json";
import { Bimp } from "./bimp";
import { SYMBOL_BITS, DEFAULT_SYMBOLS } from "./constants";

function uploadFile() {
  let fileInputElement = document.createElement("input");

  fileInputElement.setAttribute("type", "file");
  fileInputElement.style.display = "none";

  document.body.appendChild(fileInputElement);
  fileInputElement.click();
  fileInputElement.onchange = (e) => {
    let file = e.target.files[0];
    const fileReader = new FileReader();
    fileReader.readAsText(file);
    fileReader.onload = () => {
      loadChart(JSON.parse(fileReader.result));
    };
  };
  document.body.removeChild(fileInputElement);
}

function loadChart(pattern) {
  GLOBAL_STATE.chart = generateChart(pattern);
  GLOBAL_STATE.nextRow = 0;
  GLOBAL_STATE.yarnSequence = pattern.yarnSequence.pixels;
  GLOBAL_STATE.yarnPalette = pattern.yarnPalette;
  GLOBAL_STATE.leftCam = -Math.floor(GLOBAL_STATE.chart[0].length / 2);
}

function generateChart(pattern) {
  let chart = Bimp.empty(pattern.width, pattern.height, 0);
  for (const repeat of pattern.repeats) {
    let bitmap = new Bimp(
      repeat.bitmap.width,
      repeat.bitmap.height,
      repeat.bitmap.pixels
    );
    let tiled = Bimp.fromTile(
      repeat.area[0],
      repeat.area[1],
      bitmap.vFlip()
    ).vFlip();
    chart = chart.overlay(tiled, repeat.pos);
  }

  return chart.make2d().toReversed();
}

let CLIENTS = {};

let GLOBAL_STATE = {
  nextRow: 0,
  inProgressRow: -1,
  chart: generateChart(pattern),
  scale: 25,
  yarnSequence: pattern.yarnSequence.pixels,
  yarnPalette: pattern.yarnPalette,
  subscribedSid: null,
  leftCam: 0,
};

console.log(GLOBAL_STATE);

function dragCamOffset(e) {
  let startPos = e.clientX;
  let startCam = GLOBAL_STATE.leftCam;

  function move(moveEvent) {
    if (moveEvent.buttons == 0) {
      end();
    } else {
      let dx = Math.floor((startPos - moveEvent.clientX) / GLOBAL_STATE.scale);
      let newPos = startCam + dx;
      if (newPos < -100 || newPos + GLOBAL_STATE.chart[0].length > 100) return;

      GLOBAL_STATE.leftCam = newPos;
    }
  }

  function end() {
    window.removeEventListener("pointermove", move);
    window.removeEventListener("pointerup", end);
    window.removeEventListener("pointerleave", end);
  }

  window.addEventListener("pointermove", move);
  window.addEventListener("pointerup", end);
  window.addEventListener("pointerleave", end);
}

function calcYarnIndex(patternRowIndex) {
  return GLOBAL_STATE.yarnSequence[
    patternRowIndex % GLOBAL_STATE.yarnSequence.length
  ];
}

function stitchView(stitch) {
  const symbol = DEFAULT_SYMBOLS[stitch];

  return html`<div
    class="stitch"
    style="width: ${GLOBAL_STATE.scale}px; ${SYMBOL_BITS[symbol]
      ? "background: #fff"
      : ""};"></div>`;
}

function needleView(needle) {
  let needleNum = needle + GLOBAL_STATE.leftCam;
  needleNum = needleNum >= 0 ? needleNum + 1 : needleNum;

  return html`<div class="needle" style="width: ${GLOBAL_STATE.scale}px;">
    ${needleNum}
  </div>`;
}

function needleNumberView() {
  let fontSize = GLOBAL_STATE.scale - 2;
  fontSize = fontSize > 20 ? 20 : fontSize;

  return html`<div
    @pointerdown=${(e) => dragCamOffset(e)}
    class="needle-numbers"
    style="height: ${GLOBAL_STATE.scale}px;">
    <div class="row-label left"></div>
    ${Array.apply(null, Array(GLOBAL_STATE.chart[0].length)).map(
      (_, needleIndex) => needleView(needleIndex)
    )}

    <div class="row-label right"></div>
  </div>`;
}

function rowView(row, rowIndex) {
  const patternRowIndex = GLOBAL_STATE.chart.length - rowIndex - 1;
  const yarnIndex = calcYarnIndex(patternRowIndex);

  let fontSize = GLOBAL_STATE.scale - 2;
  fontSize = fontSize > 20 ? 20 : fontSize;

  return html`<div
    class="row ${GLOBAL_STATE.nextRow == patternRowIndex ? "highlighted" : ""}"
    @click=${() => {
      GLOBAL_STATE.nextRow = patternRowIndex;
      sendNextRow();
    }}
    style="background: ${GLOBAL_STATE.yarnPalette[
      yarnIndex
    ]}; height: ${GLOBAL_STATE.scale}px;">
    <div class="row-label left white" style="font-size: ${fontSize}px">
      ${patternRowIndex}
    </div>
    ${row.map((stitch) => stitchView(stitch))}

    <div class="row-label right white" style="font-size: ${fontSize}px">
      ${patternRowIndex}
    </div>
  </div>`;
}

function chartView() {
  return html`
    <div class="toolbar">
      <button @click=${() => uploadFile()}>Load KnitScape Chart</button>
      <button @click=${() => sendNextRow()}>Begin Knitting</button>
      <input
        type="range"
        @input=${(e) => {
          GLOBAL_STATE.scale = e.target.value;
        }} />
    </div>
    <div class="chart-container">
      <div class="chart">
        ${needleNumberView()}
        ${GLOBAL_STATE.chart.map((row, rowIndex) => rowView(row, rowIndex))}
        ${needleNumberView()}
      </div>
    </div>
  `;
}

function clientView(sid, clientData) {
  return html`<div class="client">
    <span>${clientData.name}</span>
    <!-- <span>${clientData.ip}</span> -->
    <!-- <span>${clientData.mac}</span> -->

    ${GLOBAL_STATE.subscribedSid == sid
      ? html`<button @click=${() => unsubscribe(sid)}>Unsubscribe</button
          ><span>connected</span>`
      : html`<button @click=${() => subscribe(sid)}>Subscribe</button>`}
  </div>`;
}

function view() {
  return html`
    <div id="clients">
      ${Object.entries(CLIENTS).map(([sid, clientData]) =>
        clientView(sid, clientData)
      )}
    </div>
    ${chartView()}
  `;
}

const socket = io("https://esphub.mehtank.com");
const list = document.getElementById("clients");

socket.on("disconnect", function () {
  console.log("Disconnected from ESPHub server");
});

socket.on("connect", function () {
  console.log("Connected to ESPHub server");
  socket.emit("enter", "membership");
  socket.emit("list");
});

socket.on("list", function (data) {
  console.log("Full list of connected ESP devices:", data);

  for (var k in data) addclient(k, data[k]);
});

socket.on("joined", function (data) {
  console.log("New ESP device(s) joined:", data);
  for (var k in data) addclient(k, data[k]);
});

socket.on("left", function (data, sid) {
  console.log("ESP device(s) left:", data);
  for (var k in data) delclient(k);
});

// socket.on("rowstart", function (data) {
//   console.log(data);
//   console.log(`row ${JSON.stringify(data)} started`);
// });

socket.on("rowfinish", function (data, sid) {
  if (sid == GLOBAL_STATE.subscribedSid) {
    console.log(`row ${data} finished`);
    GLOBAL_STATE.nextRow =
      (GLOBAL_STATE.nextRow + 1) % GLOBAL_STATE.chart.length;
    sendNextRow();
  }
});

function command(sid, event, data) {
  socket.emit("command", { sid, event, data });
  console.log(`sending event ${event} with data ${data}`);
}

function blink(sid) {
  command(sid, "blink");
}

function subscribe(sid) {
  if (GLOBAL_STATE.subscribedSid) {
    command(GLOBAL_STATE.subscribedSid, "unsubscribe");
  }
  command(sid, "subscribe");
  GLOBAL_STATE.subscribedSid = sid;
}

function unsubscribe(sid) {
  command(sid, "unsubscribe");
  GLOBAL_STATE.subscribedSid = null;
}

function sendNextRow() {
  const data = GLOBAL_STATE.chart[GLOBAL_STATE.nextRow];
  command(GLOBAL_STATE.subscribedSid, "loadrow", data);
}

socket.on("ack", function (data) {
  if (data.event == "blink") {
    var elem = document.getElementById("blink" + data.sid);
    elem.style.backgroundColor = "#14dd48";
    window.setTimeout(function () {
      var elem = document.getElementById("blink" + data.sid);
      elem.style.backgroundColor = "#dd4814";
    }, 500);
  }
});

function addclient(sid, data) {
  CLIENTS[sid] = data;
}

function delclient(sid) {
  delete CLIENTS[sid];
}

function timeSince(ts) {
  var timeStamp = new Date(ts * 1000);
  var now = new Date(),
    secondsPast = (now.getTime() - timeStamp.getTime()) / 1000;
  if (secondsPast < 60) return secondsPast + "s";
  if (secondsPast < 3600) return parseInt(secondsPast / 60) + "min";
  if (secondsPast <= 86400) return parseInt(secondsPast / 3600) + "h";
  if (secondsPast <= 2628000) return parseInt(secondsPast / 86400) + "d";
  if (secondsPast <= 31536000) return parseInt(secondsPast / 2628000) + "mo";
  if (secondsPast > 31536000) return parseInt(secondsPast / 31536000) + "y";
}

function r() {
  render(view(), document.body);

  window.requestAnimationFrame(r);
}

function init() {
  render(view(), document.body);
  loadChart(pattern);
  r();
}

window.onload = init;
