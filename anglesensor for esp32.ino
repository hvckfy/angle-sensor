#include <WiFi.h>
#include <WebServer.h>
#include <SPI.h>
#include <math.h>

const int csbPin = 5;



const char* ssid = "angle sensor";
const char* password = "esspanglesensor";

WebServer server(80);

int maxTime = 5000;
int delayTime = 1000;

void SCAwait(){
  digitalWrite(csbPin,  HIGH); 
  delayMicroseconds(150);
  digitalWrite(csbPin,LOW); 
}

String angle(){
  uint16_t RDAX,RDAY;   
  uint8_t TEMP;
  SCAwait();
  { //RDAx
    uint8_t buff[3]={0x10,0,0}; 
    SPI.transfer(buff,3); 
    RDAX=((uint16_t)buff[1]<<3)+(buff[2]>>5); 
  }
  SCAwait();
  { //RDAY
    uint8_t buff[3]={0x11,0,0}; 
    SPI.transfer(buff,3); 
    RDAY=((uint16_t)buff[1]<<3)+(buff[2]>>5); 
  }
  SCAwait();
  { //TEMP
    uint8_t buff[2]={0x8,0};  
    SPI.transfer(buff,2);  
    TEMP=buff[1];  
  }
  float floatTemp = static_cast<float>(TEMP);
  float scorr=floatTemp*(floatTemp*(floatTemp*(-0.0000005)-0.00005)+0.0032)-0.031;; //-2.4565-1.445+0.544-0.031
  digitalWrite(csbPin,HIGH);
  float SENS = 6554.0;
  float SENScomp = SENS*(1 + scorr/100);
  #define M_PI 3.14159265358979323846
  return String(asin((float)(RDAX-RDAY)/SENScomp)* (180.0 / M_PI));
  Serial.println("RDAX:"+String(RDAX)+" RDAY:"+String(RDAY)+" TEMP:"+String(TEMP)+" scorr:"+String(scorr));
}

void onRoot(){
  server.on("/", HTTP_GET, handleRoot);
}
void handleRoot(){
  server.send(200, "text/html",
  "<form action='/update' method='GET'>"
  "Max Time: <input type='text' name='maxtime' value='" + String(maxTime) + "'><br>"
  "Delay Time: <input type='text' name='delaytime' value='" + String(delayTime) + "'><br>"
  "<input type='submit' value='Submit'>"
  "</form>"+
  "<br><button onclick='getData()'>OK</button><div id='data'></div><script>function getData(){fetch('/data').then(response =>"+
  " response.text()).then(data => document.getElementById('data').innerHTML += data);}</script>");
  Serial.println("Root server is up");
}

void onUpdate(){
  server.on("/update", HTTP_GET, handleUpdate);
}
void handleUpdate(){
  if (server.hasArg("maxtime")) {
    maxTime = server.arg("maxtime").toInt();
    Serial.print("Max Time updated to: ");
    Serial.println(maxTime);
  }
  if (server.hasArg("delaytime")) {
    delayTime = server.arg("delaytime").toInt();
    Serial.print("Delay Time updated to: ");
    Serial.println(delayTime);
  }
  Serial.println("Server updated");
  handleRoot();
}

void data(){
  Serial.println("Got data request...");
  server.on("/data", HTTP_GET, []() {
    unsigned long previousMillis = 0;
    unsigned long starttime = millis();
    String result="";
    unsigned long endtime = starttime + maxTime;
    digitalWrite(csbPin,LOW);  //включаем инклинометр
    while (millis()<=endtime){
      //Serial.println(String(millis())+" "+String(endtime));
      if ((millis() - previousMillis) >= delayTime) {
        previousMillis = millis();
        result+= String(millis()-starttime) + ";" + angle() + "<br>";
      }else {

      }
    }
    server.send(200, "text/plain", result);
    Serial.println("Data sent.");
    Serial.println("Data:");
    Serial.println(result);
  });
}

void SCA103TInit(){
  pinMode (csbPin, OUTPUT);
  SPI.begin();
  SPI.setBitOrder(MSBFIRST);
  SPI.setDataMode(SPI_MODE0);
  delay(1000);
}

void wifiInit(){
  WiFi.softAP(ssid, password);
  Serial.println("WiFi! created");
  Serial.print("IP Address: ");
  Serial.println(WiFi.softAPIP());
}

void setup() {
  Serial.begin(115200);
  
  SCA103TInit();

  wifiInit();

  onRoot();
  
  onUpdate();

  data();

  server.begin();
}

void loop() {
  server.handleClient();
}