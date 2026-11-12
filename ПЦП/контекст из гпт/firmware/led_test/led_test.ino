#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <ESPmDNS.h>
#include <FastLED.h>

const char* HOME_SSID = "YOUR_WIFI_SSID";
const char* HOME_PASS = "YOUR_WIFI_PASSWORD";
const char* WIFI_NAME = "WaterVortex";
const char* WIFI_PASS = "CHANGE_ME";

#define PUMP_PIN    25
#define PUMP_FREQ   20000
#define PUMP_MIN    148
#define PUMP_MAX    255

#define LED_PIN     16
#define NUM_LEDS    20
#define COLOR_ORDER BRG

bool pumpOn = false;
int  pumpSpeed = 50;
int  pumpDuty = 0;
int  ledBri = 100;
int  ledMode = 0;
uint8_t ledHue = 160;

CRGB leds[NUM_LEDS];
AsyncWebServer server(80);

const char PAGE[] = R"rawliteral(
<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Водяной вихрь</title>
<style>
body{font-family:sans-serif;background:#0d1b2a;color:#e0e6ed;padding:20px;max-width:420px;margin:auto}
h1{font-size:22px;text-align:center}
.card{background:#1b263b;border-radius:14px;padding:16px;margin-bottom:16px}
label{display:block;margin:12px 0 6px}
input[type=range]{width:100%}
button{width:100%;padding:14px;font-size:18px;border:0;border-radius:10px;background:#415a77;color:#fff}
button.on{background:#2a9d8f}
select{width:100%;height:40px;border-radius:8px;border:0}
#hu{-webkit-appearance:none;appearance:none;height:32px;border-radius:16px;outline:none;
background:linear-gradient(to right,#f00,#ff0,#0f0,#0ff,#00f,#f0f,#f00)}
#hu::-webkit-slider-thumb{-webkit-appearance:none;width:34px;height:34px;border-radius:50%;
background:#fff;border:3px solid #0d1b2a;box-shadow:0 0 6px #000}
#hu::-moz-range-thumb{width:28px;height:28px;border-radius:50%;background:#fff;border:3px solid #0d1b2a}
#sw{height:14px;border-radius:7px;margin-top:10px}
</style></head><body>
<h1>🌀 Водяной вихрь</h1>
<div class="card">
<button id="pw" onclick="togglePump()">Насос: выкл</button>
<label>Скорость: <span id="sv"></span>%</label>
<input type="range" id="sp" min="0" max="100" oninput="send()">
</div>
<div class="card">
<label>Режим подсветки</label>
<select id="md" onchange="send()">
<option value="0">Один цвет</option>
<option value="1">Радуга</option>
<option value="2">Цвет по скорости</option>
<option value="3">Бегущий огонь</option>
</select>
<div id="hb">
<label>Цвет</label>
<input type="range" id="hu" min="0" max="255" oninput="send()">
<div id="sw"></div>
</div>
<label>Яркость: <span id="bv"></span></label>
<input type="range" id="br" min="0" max="255" oninput="send()">
</div>
<script>
let on=false;
function $(i){return document.getElementById(i)}
function show(){$('pw').textContent='Насос: '+(on?'вкл':'выкл');$('pw').className=on?'on':'';
$('sv').textContent=$('sp').value;$('bv').textContent=$('br').value;
let m=$('md').value;$('hb').style.display=(m=='0'||m=='3')?'block':'none';
$('sw').style.background='hsl('+Math.round($('hu').value*360/256)+',100%,50%)'}
let busy=false,pending=false;
function send(){show();
if(busy){pending=true;return}
busy=true;
fetch('/set?on='+(on?1:0)+'&sp='+$('sp').value+'&br='+$('br').value+
'&md='+$('md').value+'&hu='+$('hu').value)
.finally(()=>{busy=false;if(pending){pending=false;send()}})}
function togglePump(){on=!on;send()}
fetch('/state').then(r=>r.json()).then(s=>{on=s.on;$('sp').value=s.sp;$('br').value=s.br;
$('md').value=s.md;$('hu').value=s.hu;show()});
</script></body></html>
)rawliteral";

void handleRoot(AsyncWebServerRequest *r) {
  r->send(200, "text/html; charset=utf-8", PAGE);
}

void handleSet(AsyncWebServerRequest *r) {
  if (r->hasParam("on")) pumpOn = r->getParam("on")->value() == "1";
  if (r->hasParam("sp")) pumpSpeed = constrain(r->getParam("sp")->value().toInt(), 0, 100);
  if (r->hasParam("br")) ledBri = constrain(r->getParam("br")->value().toInt(), 0, 255);
  if (r->hasParam("md")) ledMode = constrain(r->getParam("md")->value().toInt(), 0, 3);
  if (r->hasParam("hu")) ledHue = constrain(r->getParam("hu")->value().toInt(), 0, 255);
  r->send(200, "text/plain", "ok");
}

void handleState(AsyncWebServerRequest *r) {
  char buf[100];
  snprintf(buf, sizeof(buf),
    "{\"on\":%s,\"sp\":%d,\"br\":%d,\"md\":%d,\"hu\":%d}",
    pumpOn ? "true" : "false", pumpSpeed, ledBri, ledMode, ledHue);
  r->send(200, "application/json", buf);
}

void updatePump() {
  static unsigned long t = 0;
  if (millis() - t < 15) return;
  t = millis();
  int target = pumpOn ? map(pumpSpeed, 0, 100, PUMP_MIN, PUMP_MAX) : 0;
  if (target == 0) pumpDuty = 0;
  else if (pumpDuty < target) pumpDuty = max(pumpDuty + 1, PUMP_MIN);
  else if (pumpDuty > target) pumpDuty--;
  ledcWrite(PUMP_PIN, pumpDuty);
}

void updateLeds() {
  static unsigned long t = 0;
  static uint8_t hue = 0;
  static uint8_t hueStep = 0;
  static int curBri = 0;
  if (millis() - t < 10) return;
  t = millis();

  if (curBri < ledBri) curBri += max(1, (ledBri - curBri) / 12);
  else if (curBri > ledBri) curBri -= max(1, (curBri - ledBri) / 12);

  if (ledMode == 0) fill_solid(leds, NUM_LEDS, CHSV(ledHue, 255, 255));
  if (ledMode == 1) {
    if (++hueStep >= 3) { hueStep = 0; hue++; }
    fill_rainbow(leds, NUM_LEDS, hue, 255 / NUM_LEDS);
  }
  if (ledMode == 2) {
    uint8_t h = map(pumpSpeed, 0, 100, 160, 0);
    fill_solid(leds, NUM_LEDS, CHSV(h, 255, 255));
  }
  if (ledMode == 3) {
    static uint8_t pos = 0, stepT = 0;
    if (++stepT >= 4) { stepT = 0; pos = (pos + 1) % NUM_LEDS; }
    fadeToBlackBy(leds, NUM_LEDS, 40);
    leds[pos] = CHSV(ledHue, 255, 255);
  }
  FastLED.setBrightness(fl::dim8_video(curBri));

  static CRGB lastLeds[NUM_LEDS];
  static int lastBri = -1;
  int bri = FastLED.getBrightness();
  if (bri == lastBri && ::memcmp(leds, lastLeds, sizeof(leds)) == 0) return;
  ::memcpy(lastLeds, leds, sizeof(leds));
  lastBri = bri;
  FastLED.show();
}

void setupWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.setAutoReconnect(true);

  Serial.println("Сети, которые видит ESP32:");
  int n = WiFi.scanNetworks();
  for (int i = 0; i < n; i++) {
    Serial.printf("  %s  (сигнал %d)\n", WiFi.SSID(i).c_str(), WiFi.RSSI(i));
  }

  WiFi.begin(HOME_SSID, HOME_PASS);
  WiFi.setTxPower(WIFI_POWER_8_5dBm);
  Serial.print("Подключаюсь к домашнему Wi-Fi");
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Готово! Адрес: http://");
    Serial.println(WiFi.localIP());
  } else {
    WiFi.mode(WIFI_AP);
    WiFi.softAP(WIFI_NAME, WIFI_PASS);
    WiFi.setTxPower(WIFI_POWER_8_5dBm);
    Serial.print("Домашняя сеть не найдена. Своя сеть: ");
    Serial.println(WIFI_NAME);
    Serial.print("Адрес: http://");
    Serial.println(WiFi.softAPIP());
  }

  MDNS.begin("vortex");
  Serial.println("Или: http://vortex.local");
}

void setup() {
  Serial.begin(115200);
  ledcAttach(PUMP_PIN, PUMP_FREQ, 8);
  ledcWrite(PUMP_PIN, 0);
  FastLED.addLeds<WS2811, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS);

  setupWiFi();

  server.on("/", HTTP_GET, handleRoot);
  server.on("/set", HTTP_GET, handleSet);
  server.on("/state", HTTP_GET, handleState);
  server.begin();
}

void loop() {
  updatePump();
  updateLeds();

  static unsigned long lastCheck = 0;
  if (WiFi.getMode() == WIFI_STA && millis() - lastCheck > 10000) {
    lastCheck = millis();
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("Wi-Fi пропал, переподключаюсь...");
      WiFi.reconnect();
    }
  }
}
