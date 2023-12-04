"use strict";
import { io } from "socket.io-client";
import { html, render } from "lit-html";
import pattern from "./pattern.json";
import { Bimp } from "./bimp";
import { SYMBOL_BITS, SYMBOL_PATHS, DEFAULT_SYMBOLS } from "./constants";

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

let chartCanvas;
let overlayCanvas;

let CLIENTS = {};

let GLOBAL_STATE = {
  nextRow: 0,
  inProgressRow: -1,
  chart: generateChart(pattern),
  scale: 25,
  yarnSequence: pattern.yarnSequence.pixels,
  yarnPalette: pattern.yarnPalette,
  subscribedSid: null,
};

console.log(GLOBAL_STATE);

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

function rowView(row, rowIndex) {
  const patternRowIndex = GLOBAL_STATE.chart.length - rowIndex - 1;
  const yarnIndex = calcYarnIndex(patternRowIndex);

  return html`<div
    class="row ${GLOBAL_STATE.nextRow == patternRowIndex ? "highlighted" : ""}"
    @click=${() => {
      GLOBAL_STATE.nextRow = patternRowIndex;
      sendNextRow();
    }}
    style="background: ${GLOBAL_STATE.yarnPalette[yarnIndex]}; height: ${
    GLOBAL_STATE.scale
  }px;">
    <div class="row-label" style="font-size: ${GLOBAL_STATE.scale - 2}px">
      ${patternRowIndex}
    </div>
      ${row.map((stitch) => stitchView(stitch))}
      </div>
    </div>
  </div>`;
}

function chartView() {
  return html`
    <button @click=${() => sendNextRow()}>Begin Knitting</button>
    <div class="chart-container">
      <div class="chart">
        ${GLOBAL_STATE.chart.map((row, rowIndex) => rowView(row, rowIndex))}
      </div>
    </div>
  `;
}

function clientView(sid, clientData) {
  return html`<div>
    <span>${clientData.name}</span>
    <span>${clientData.ip}</span>
    <span>${clientData.mac}</span>

    <button @click=${() => subscribe(sid)}>Subscribe</button>
  </div>`;
}

function view() {
  return html`<div id="clients">
      ${Object.entries(CLIENTS).map(([sid, clientData]) =>
        clientView(sid, clientData)
      )}
    </div>
    ${chartView()}`;
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

socket.on("left", function (data) {
  console.log("ESP device(s) left:", data);
  for (var k in data) delclient(k);
});

socket.on("rowstart", function (data) {
  console.log(data);
  console.log(`row ${JSON.stringify(data)} started`);
});

socket.on("rowfinish", function (data) {
  console.log(`row ${data} finished`);
  GLOBAL_STATE.nextRow = GLOBAL_STATE.nextRow + 1;
  sendNextRow();
});

function blink(sid) {
  var data = {
    event: "blink",
    sid: sid,
  };
  socket.emit("command", data);
  console.log("Sending command: ", data);
}

function subscribe(sid) {
  var data = {
    event: "subscribe",
    sid: sid,
  };
  socket.emit("command", data);
  console.log("Sending command: ", data);
  GLOBAL_STATE.subscribedSid = sid;
}

function sendNextRow() {
  const data = GLOBAL_STATE.chart[GLOBAL_STATE.nextRow];
  const row = {
    event: "loadrow",
    sid: GLOBAL_STATE.subscribedSid,
    data,
  };

  socket.emit("command", row);
  console.log(`forwarding data: ${data}`);
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
  r();
}

window.onload = init;
